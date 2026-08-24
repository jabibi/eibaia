const shortDateFormatter = new Intl.DateTimeFormat("es-ES", { day: "2-digit", month: "short" });
const shortDateWithYearFormatter = new Intl.DateTimeFormat("es-ES", {
  day: "2-digit",
  month: "short",
  year: "numeric",
});

/** Formatea una fecha ISO ("YYYY-MM-DD") de forma corta y local, p. ej. "23 ago" — o
 * "23 ago 2025" cuando el año no es el actual, para no perder esa información en tablas
 * que puedan mostrar movimientos de años anteriores. */
export function formatShortDate(isoDate: string): string {
  const date = new Date(`${isoDate}T00:00:00`);
  const formatter = date.getFullYear() === new Date().getFullYear() ? shortDateFormatter : shortDateWithYearFormatter;
  return formatter.format(date);
}
