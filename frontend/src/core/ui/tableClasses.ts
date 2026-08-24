export const tableHeaderCellClass = "px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500";

export const tableRowClass = "border-b border-slate-100 transition-colors last:border-0 hover:bg-slate-50/50";

export const tableCellClass = "px-4 py-3 align-middle text-slate-700";

// Para columnas de importe: alineado a la derecha (el € siempre en la misma vertical) y con
// `font-mono` + `tabular-nums` (ancho fijo por carácter) para que los dígitos y la coma
// decimal queden alineados verticalmente fila a fila, el estándar en tablas financieras.
export const tableCellAmountClass = `${tableCellClass} text-right font-mono tabular-nums`;
