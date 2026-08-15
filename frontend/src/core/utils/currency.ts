const formatter = new Intl.NumberFormat("es-ES", {
  style: "currency",
  currency: "EUR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function formatCurrency(amountCents: number): string {
  return formatter.format(amountCents / 100);
}

export function euroToCents(amount: number): number {
  return Math.round(amount * 100);
}
