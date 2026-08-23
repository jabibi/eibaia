export const tableHeaderCellClass = "px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500";

export const tableRowClass = "border-b border-slate-100 transition-colors last:border-0 hover:bg-slate-50/50";

export const tableCellClass = "px-4 py-3 align-middle text-slate-700";

// Para columnas de importe: alineado a la derecha (el € siempre en la misma vertical) y con
// `tabular-nums` (todas las cifras del mismo ancho fijo, en vez del ancho proporcional por
// defecto) para que la coma decimal también quede en la misma vertical fila a fila.
export const tableCellAmountClass = `${tableCellClass} text-right tabular-nums`;
