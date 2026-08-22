# ElosuE! — Notas para Claude Code

Consulta también `README.rst` para la descripción general del stack, roles/permisos y estructura del repo.

## Librería de UI reutilizable (`frontend/src/core/components/ui/`)

Antes de construir un formulario o tabla nuevos, revisa si ya hay un componente aquí que lo
resuelva. La idea es que el aspecto visual (padding, bordes, colores de foco, radios, etc.)
viva en un solo sitio y no se repita como clases de Tailwind sueltas copiadas en cada vista —
así un cambio de estilo se aplica en toda la app editando un único archivo.

Componentes disponibles:

- `Card.vue` — tarjeta blanca con borde y sombra suave.
- `FormField.vue` — label en mayúsculas + slot para el control.
- `FormInput.vue` — `<input>` con `v-model`, tamaño compacto estándar de formulario.
- `FormSelect.vue` — `<select>` con `v-model`, más denso (pensado para filas de tabla).
- `SegmentedControl.vue` — pastillas tipo toggle (ej. Gasto/Ingreso/Ajuste).
- `TabNav.vue` — pestañas de borde inferior (ej. filtros Activos/Nuevos/Inactivos).
- `ToggleSwitch.vue` — interruptor compacto accesible.
- `StatusBadge.vue` — badge de estado, `variant="neutral"` (por defecto) / `"success"` / `"warning"`.
- `KpiCard.vue` — tarjeta-enlace de KPI (borde + sombra + hover + foco), `variant="default"`
  (por defecto, hover verde) / `"warning"` (hover ámbar) / `"danger"` (borde y foco rojos). Solo
  envuelve el "cascarón" — el contenido (título, valor, hint) va por slot porque varía mucho
  entre tarjetas.
- `TableIconAction.vue` — botón/enlace de solo icono para filas de tabla (editar/confirmar/
  eliminar), con `title`+`aria-label` automáticos a partir de `label` y `tone="neutral"`
  (por defecto) / `"success"` / `"danger"`.
- `Button.vue` — botón con `variant="primary"` (por defecto) / `"secondary"` / `"danger"`, más
  `icon` (nombre de icono Iconify, ej. `"lucide:log-out"`, ver sección de iconos más abajo) y
  `loading` (spinner + disabled) opcionales.
- `ColorPicker.vue` — cuadrícula de 12 swatches circulares (`v-model` de tipo `LabelColor`, ver
  `frontend/src/core/ui/labelColors.ts`) para elegir un color entre un set fijo predefinido. Usado
  para el color de las etiquetas de movimientos (`pages/finance/labels.vue`).
- `ColorSelect.vue` — `<select>` nativo pero con cada `<option>` teñido por su propio color
  (`options: { value, label, color }[]`) y un punto de color en el propio control cuando está
  cerrado. Usado para elegir la etiqueta de un movimiento en `MovementForm.vue`. Deliberadamente
  nativo (no un listbox/combobox custom) para mantener accesibilidad de teclado y el picker móvil
  del sistema — mismo criterio que el resto de la librería (ver sección sobre PrimeVue más abajo).

Constantes de estilo para tablas nativas en `frontend/src/core/ui/tableClasses.ts`:
`tableHeaderCellClass`, `tableRowClass`, `tableCellClass`. No hay un componente `<Table>`
genérico porque la estructura de columnas varía mucho entre vistas — estas clases son el
punto único de verdad para cabeceras y filas.

Referencias de uso ya migradas a esta librería:
`frontend/src/modules/finance/components/MovementForm.vue` y
`frontend/src/pages/{index,pending,settings/reset,finance/transactions}.vue` (botones),
`frontend/src/modules/finance/components/MovementList.vue` y
`frontend/src/modules/users/views/UsersAdmin.vue` (tablas).

**Pendiente / a completar más adelante:** esta librería está en marcha, no cerrada. Está
pensada para irse ampliando según aparezcan necesidades reales en nuevas vistas, no para
anticipar variantes que nadie ha pedido todavía. Amplíala cuando haga falta en vez de volver a
duplicar clases sueltas en el sitio de uso.

## Desarrollo local con backend real (`npm run dev`)

`frontend/.env` lleva `NUXT_PUBLIC_API_BASE=/api` porque ese es el valor correcto para
despliegue (rewrite de Firebase Hosting a la Cloud Function). `nuxt dev` no tiene ese
rewrite, así que si necesitas el backend real corriendo en local (`cd functions && venv/bin/uvicorn
app.main:app --port 8000 --reload`), **no edites `frontend/.env`** para apuntar a
`http://localhost:8000/api` — ese archivo se lee también en build time y `npm run generate`
horneraría esa URL de local en el bundle de despliegue (ver también el runbook de
`npm run generate` sobre este mismo footgun). En su lugar, pasa la variable solo para ese
arranque puntual del proceso:

```bash
NUXT_PUBLIC_API_BASE=http://localhost:8000/api npm run dev
```

## Comprobar tipos (`npm run typecheck`)

`frontend/tsconfig.json` (extiende `.nuxt/tsconfig.json`) y las devDependencies
`typescript`/`vue-tsc` están explícitas en `package.json` — no vengan por defecto con el
scaffold de este repo, así que si algún día faltan (`npm run typecheck` falla con un
`ERR_PACKAGE_PATH_NOT_EXPORTED` o similar, o directamente no existe el script), es que se han
perdido esas piezas, no que haya que instalar `vue-tsc` suelto con `npx` (eso trae una copia
de `typescript` incompatible con la que ya usa el resto del árbol — mejor fijarlo como
devDependency, deduplicado con la versión que ya resuelven `nuxt`/`vue`/`pinia`, y comprobarlo
con `npm ls typescript`).

**`typescript` está tope en la v6.x a propósito — no subir a v7 todavía.** TypeScript 7
reestructuró el mapa de `exports` de su `package.json` y quitó el subpath `./lib/tsc` que
`vue-tsc` usa internamente para localizar el compilador. Con `typescript@7.0.2` instalado,
`npm run typecheck` no da un error de tipos — **explota el propio proceso** con
`Error [ERR_PACKAGE_PATH_NOT_EXPORTED]: Package subpath './lib/tsc' is not defined by "exports"`
antes de analizar una sola línea (probado en la práctica: `npm install typescript@latest` con
`vue-tsc@3.3.11`, que era su última versión disponible en ese momento). No es un problema de
código de este repo, es que `vue-tsc` aún no soporta el nuevo `exports` de TS7. Antes de volver
a intentar esta subida, comprueba que ya existe una versión de `vue-tsc` que arregle esto
(changelog/issues de `vue-tsc` en GitHub) — si no, `npm install typescript@latest` fallará en
seco igual que ahora y hay que revertir a `typescript@^6` (`npm install typescript@^6`).

## Comprobar tipos en Python (Pyright)

El backend (`functions/`) no tiene ningún linter/type-checker instalado como dependencia — ni
`mypy` ni `pyright` están en `requirements.txt`, y no hay que añadirlos ahí. Se ejecuta al vuelo
vía `npx` (usa el Node del propio repo, no hace falta instalar nada globalmente), apuntando al
intérprete del `venv/` para que resuelva `firebase_admin`/`fastapi`/`pydantic` igual que en
tiempo de ejecución:

```bash
cd functions
npx --yes pyright --pythonpath venv/bin/python app main.py scripts
```

Esto es exactamente lo que hace Pylance por debajo (es el mismo motor), así que sirve como
sustituto en CLI de "revisar con Pylance".

**Ruido conocido, no son bugs reales** — a día de hoy la pasada limpia da ~14 errores que son
huecos de los *stubs* de `firebase_admin`/`firebase_functions`, no del código de este repo:
`firestore.SERVER_TIMESTAMP` / `Increment` / `FieldFilter` / `Query` ("not a known attribute of
module") y `firebase_functions.https_fn.Request`/`Response` ("not exported from module") — todos
existen y funcionan en tiempo de ejecución, Pyright solo no los ve porque esos paquetes no
publican tipos completos. Si al ejecutar Pyright aparecen *más* errores de estos que antes, no
es señal de alarma por sí sola — compara contra esta lista antes de reportarlo como regresión.

Un patrón que sí era un bug real y ya está corregido: `doc.to_dict()` de Firestore tipa como
`dict | None` (devuelve `None` si el snapshot es de un documento que no existe), y varios sitios
lo usaban sin comprobarlo. Está blindado en `app/core/firebase.py` con `snapshot_data(doc)`
— lanza un `ValueError` claro en vez de dejar que reviente más adelante con un `AttributeError`
opaco. Usa siempre `snapshot_data(doc)` en vez de `doc.to_dict()` a pelo cuando ya sepas que el
documento existe (tras un `.exists`, un resultado de `.stream()`, o justo después de escribirlo).

Ejecútalo tras cambios en `functions/app/**/*.py` con lógica no trivial (igual que
`npm run typecheck` en el frontend) — no hace falta para scripts sueltos en `scripts/`.

## SEO/Open Graph: tiene que vivir en `nuxt.config.ts`, no en `app.vue`

Con `ssr: false`, `nuxt generate` prerrenderiza cada ruta pero **no** ejecuta el árbol de
componentes Vue para generar contenido — solo copia el shell SPA (confirmado: el aviso
"HTML content not prerendered because ssr: false was set" que suelta el build es literal).
Esto significa que un `useSeoMeta`/`useHead` llamado desde un componente (p. ej. `app.vue`)
**no aparece en el HTML estático** que se sirve — solo se aplica tras la hidratación en el
cliente. Para un usuario normal esto da igual (el JS carga enseguida), pero WhatsApp/Facebook/
Twitter no ejecutan JS al generar la tarjeta de previsualización de un enlace: verían la página
sin ninguna etiqueta `og:*`.

Por eso las etiquetas Open Graph/Twitter/canonical de `frontend/nuxt.config.ts` están en
`app.head.meta`/`app.head.link` (config de build, sí se hornea en el HTML) y no en un
`useSeoMeta()` dentro de `app.vue`. El título de pestaña por página (`useHead({ title: ... })`
en cada página) sí puede ir en un componente porque solo afecta al `document.title` en el
navegador del usuario, no a un crawler sin JS — verificado comparando el HTML generado
(`frontend/.output/public/index.html`) antes y después de mover el bloque OG.

Ejecuta `npm run typecheck` tras cambios en `.ts`/`.vue` con lógica no trivial (no hace falta
para cambios puramente de estilos/Tailwind).

## PrimeVue: eliminado por completo

El proyecto usó `primevue`/`@primevue/nuxt-module` durante un tiempo, pero solo por dos
**directivas** (`v-tooltip` en el sidebar, `ripple: true` en `nuxt.config.ts`) — ningún
componente visual de PrimeVue se usaba ya en ninguna plantilla (ver el porqué histórico más
abajo). Se ha desinstalado del todo (`primevue`, `@primevue/nuxt-module`, `@primeuix/themes`,
incluida la entrada en `modules` y el bloque `primevue: {...}` de `nuxt.config.ts`).

- `v-tooltip.right="expr"` → atributo nativo `:title="expr"`. Ojo con tipos: si `expr` puede
  ser `string | null` (p. ej. `authStore.user?.email`, que Firebase tipa como `string | null`),
  hace falta `?? undefined` — `:title` solo acepta `string | undefined`, no `null`. El
  `aria-label` de cada elemento, que ya existía por separado (necesario porque el sidebar
  colapsado en icon-only depende de él para el nombre accesible), no cambia — sigue siendo la
  fuente real para lectores de pantalla; `title` es solo el tooltip visual al pasar el ratón.
- `ripple: true` no se usaba en ninguna plantilla (`grep -rn "v-ripple" frontend/src` no daba
  ningún resultado antes de quitarlo), así que no hizo falta ningún reemplazo visual.

### Por qué no se usaban ya sus componentes

Históricamente `nuxt-primevue` envolvía sus estilos en `@layer primevue`, pero el
preflight/reset de Tailwind de este proyecto no vivía en una capa nombrada equivalente — así
que el reset de Tailwind ganaba siempre sobre PrimeVue (padding, border-width, etc. de
`.p-button`, `.p-inputtext`, `.p-dropdown`... quedaban a 0). Por eso toda la UI ya usaba
elementos nativos + Tailwind vía la librería de componentes de arriba antes incluso de
desinstalar el paquete — `frontend/src/assets/css/main.css` nunca necesitó ningún parche
`!important` de PrimeVue.

Si alguna vez se reintroduce PrimeVue (o cualquier librería de componentes) para algo
concreto: ten en cuenta que un componente propio (p. ej. `Button.vue`) puede colisionar de
nombre con un registro global de esa librería (el import local gana dentro de una SFC, pero
`<component :is="'Button'">` con string dinámico sí resolvería contra el registro global); y
que la v5 de `primevue`/`@primeuix/themes` mete un gate de licencia comercial obligatorio
(`@primeui/license-manager`) que pinta un banner rojo "Invalid PrimeUI License" en pantalla si
no hay clave configurada, pase lo que pase — la v4 no lo tenía.

## Iconos: Nuxt Icon + Iconify (Lucide), no PrimeIcons

`primeicons` fue sustituido por `@nuxt/icon` (componente `<Icon name="...">`, auto-importado)
con los sets `@iconify-json/lucide` (prefijo `lucide:`, el set por defecto para iconos
genéricos), `@iconify-json/logos` (prefijo `logos:`, solo para logos de marca reales con color
fijo — hoy únicamente `logos:google-icon` en el botón de login) y `@iconify-json/simple-icons`
(prefijo `simple-icons:`, logos de marca monocromos que respetan `currentColor` — usado en
`simple-icons:github` en vez de `logos:github`, precisamente para que el hover
`text-slate-400 → hover:text-slate-700` del enlace de GitHub siga funcionando).

Antes de usar un nombre de icono, comprueba que existe en el set instalado en vez de adivinar
(los nombres de Lucide han cambiado entre versiones — p. ej. el canónico es `circle-check-big`,
no `check-circle`; `house`, no `home`):

```bash
node -e "console.log('circle-check-big' in require('@iconify-json/lucide/icons.json').icons)"
```

**⚠️ Nuxt Icon usa modo `css` por defecto** (renderiza `<span class="iconify i-lucide:x">` con
`mask-image`, no SVG inline), y esa CSS se inyecta **sin `@layer`**. Con Tailwind v4 (que sí
envuelve sus propias utilidades en `@layer utilities`), una regla sin capa siempre gana sobre
una regla en capa — así que sin configurar esto, algo tan básico como `md:hidden` en un
`<Icon>` deja de funcionar (el icono se queda visible siempre, en cualquier breakpoint). Esto
ya está resuelto en `frontend/src/app.config.ts`:

```ts
export default defineAppConfig({
  icon: { mode: "css", cssLayer: "base" },
});
```

Eso mete la CSS de los iconos en `@layer base`, que Tailwind sitúa por debajo de `utilities` —
así cualquier utilidad de Tailwind (incluidas las responsive) puede seguir sobreescribiéndola.
Si algún día un icono no responde a una clase de Tailwind (tamaño, `hidden`, color...), esto es
lo primero a revisar.

## Tailwind CSS v4: plugin de Vite directo, sin `@nuxtjs/tailwindcss`

`@nuxtjs/tailwindcss` fija `tailwindcss: ~3.4.17` como dependencia dura y solo da soporte
experimental a v4 (avisa por consola si detecta v4 instalado). Con Tailwind v4 se usa en su
lugar el plugin oficial `@tailwindcss/vite` directamente en `nuxt.config.ts`
(`vite: { plugins: [tailwindcss()] }`), sin módulo Nuxt de por medio. Ya no hay
`tailwind.config.ts` (v4 detecta el contenido automáticamente y la personalización de tema se
hace con `@theme` en CSS si algún día hace falta) ni directivas `@tailwind base/components/utilities`
— `frontend/src/assets/css/main.css` es solo `@import "tailwindcss";`.

## Nuxt 4: `public/` ya no es relativo a `srcDir`

Este proyecto fija `srcDir: "src/"`, así que en Nuxt 3 la carpeta de assets estáticos vivía en
`frontend/src/public/`. En Nuxt 4 el directorio `public` (igual que `server/`) se resuelve
siempre relativo a la raíz del proyecto (`rootDir`), **no** a `srcDir` — es un cambio de
convención explícito de la v4 (separar lo que es "app", dentro de `srcDir`, de lo que es
infraestructura de proyecto). Por eso la carpeta se movió a `frontend/public/` (fuera de
`src/`). Si algún asset estático (favicon, imágenes de `public/img/...`) empieza a devolver el
HTML de fallback de la SPA en vez del propio fichero, es señal de que algo volvió a vivir bajo
`src/public/` por error.
