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
- `Button.vue` — botón con `variant="primary"` (por defecto) / `"secondary"` / `"danger"`, más
  `icon` (clase de PrimeIcons) y `loading` (spinner + disabled) opcionales.

  ⚠️ **Ojo con el nombre:** `nuxt-primevue` registra globalmente un componente distinto también
  llamado `Button` (el de PrimeVue). Como ya no usamos ningún componente de PrimeVue en plantillas
  (ver más abajo), no debería aparecer por accidente — pero si algún día se reintroduce un
  `<Button>` de PrimeVue en algún sitio, importa el nuestro explícitamente
  (`import Button from "~/core/components/ui/Button.vue"`) en ese archivo: el import local
  siempre gana sobre el registro global dentro de esa SFC. Nunca lo invoques vía
  `<component :is="'Button'">` (string dinámico) — ahí sí se resolvería contra el registro
  global y podría coger el de PrimeVue en vez del nuestro (es la misma causa raíz del bug del
  botón de logout que salía azul: ver historial de este archivo).

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

Ejecuta `npm run typecheck` tras cambios en `.ts`/`.vue` con lógica no trivial (no hace falta
para cambios puramente de estilos/Tailwind).

## Por qué no usamos componentes de PrimeVue para esto

`nuxt-primevue` envuelve sus estilos en `@layer primevue`, pero el preflight/reset de
Tailwind de este proyecto no vive en una capa nombrada equivalente — así que el reset de
Tailwind gana siempre sobre PrimeVue (padding, border-width, etc. de `.p-button`,
`.p-inputtext`, `.p-dropdown`... quedan a 0, independientemente del orden de los `css:` en
`nuxt.config.ts`). Para UI nueva es más simple y fiable usar elementos nativos + Tailwind vía
la librería de arriba, evitando este problema de raíz en vez de parchearlo caso a caso.

Ya no queda ningún `<Button>`/`<DataTable>`/`<Column>`/`<Tag>`/`<Dropdown>`/`<SelectButton>` de
PrimeVue en ninguna plantilla — todos migrados a `ui/Button.vue`, `ui/StatusBadge.vue` y tablas
nativas con `tableClasses.ts` (`frontend/src/assets/css/main.css` ya no tiene ningún parche
`!important` de PrimeVue, quedó limpio). El módulo `nuxt-primevue` se mantiene igualmente
instalado y activo solo por sus **directivas** (`v-tooltip` en el sidebar, `ripple: true` en
`nuxt.config.ts`) — esas no chocan con el preflight de Tailwind del mismo modo que los
componentes, así que no necesitan parche. Si en el futuro se vuelve a introducir un componente
de PrimeVue en una plantilla, recuerda que su nombre puede colisionar con el de un componente
propio (ver aviso sobre `Button.vue` arriba) y que probablemente reaparezca la necesidad de un
parche `!important` en `main.css` para ese componente en concreto.
