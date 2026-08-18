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
- `StatusBadge.vue` — badge neutro para estados.
- `AppButton.vue` — botón con `variant="primary"` o `"secondary"`.

Constantes de estilo para tablas nativas en `frontend/src/core/ui/tableClasses.ts`:
`tableHeaderCellClass`, `tableRowClass`, `tableCellClass`. No hay un componente `<Table>`
genérico porque la estructura de columnas varía mucho entre vistas — estas clases son el
punto único de verdad para cabeceras y filas.

Referencias de uso ya migradas a esta librería:
`frontend/src/modules/finance/components/MovementForm.vue` (formulario) y
`frontend/src/modules/users/views/UsersAdmin.vue` (tabla).

**Pendiente / a completar más adelante:** esta librería está en marcha, no cerrada. Está
pensada para irse ampliando según aparezcan necesidades reales en nuevas vistas, no para
anticipar variantes que nadie ha pedido todavía. Ejemplos de huecos previsibles: variantes de
`StatusBadge` (éxito/peligro, no solo neutro), un `AppButton` con severidad `danger` (para
acciones destructivas tipo "Restablecer aplicación"), y un componente de tabla más genérico
si el patrón de columnas se repite igual en varias vistas. Amplíala cuando haga falta en vez
de volver a duplicar clases sueltas en el sitio de uso.

## Por qué no usamos componentes de PrimeVue para esto

`nuxt-primevue` envuelve sus estilos en `@layer primevue`, pero el preflight/reset de
Tailwind de este proyecto no vive en una capa nombrada equivalente — así que el reset de
Tailwind gana siempre sobre PrimeVue (padding, border-width, etc. de `.p-button`,
`.p-inputtext`, `.p-dropdown`... quedan a 0, independientemente del orden de los `css:` en
`nuxt.config.ts`). Hay parches puntuales con `!important` en `frontend/src/assets/css/main.css`
para los `Button`/`Dropdown`/`SelectButton` de PrimeVue que todavía se usan en el resto de la
app (login, pending, reset). Para UI nueva es más simple y fiable usar elementos nativos +
Tailwind vía la librería de arriba, evitando este problema de raíz en vez de parchearlo caso
a caso.
