import { getReport, getSummary, listCashboxes, listCategories, type FinanceSummary } from "~/modules/finance/api";
import { currentMonthRange } from "~/core/utils/dateRange";
import { getUsersSummary, type UsersSummary } from "~/modules/users/api";

// Recursos crudos que comparten varios KPIs (p. ej. 4 KPIs de Caja se sirven todos del mismo
// GET /finance/summary). Cada uno memoiza su promesa en curso para que, dentro de un mismo
// pase de carga (ver loadKpiProps), pedir el mismo recurso desde varios KPIs a la vez no
// dispare varias peticiones de red — solo la primera llamada hace fetch, el resto reutiliza
// esa misma promesa.
let financeSummaryPromise: Promise<FinanceSummary> | null = null;
function loadFinanceSummary(): Promise<FinanceSummary> {
  financeSummaryPromise ??= getSummary();
  return financeSummaryPromise;
}

let categoryCountPromise: Promise<number> | null = null;
function loadCategoryCount(): Promise<number> {
  categoryCountPromise ??= listCategories().then((result) => result.categories.length);
  return categoryCountPromise;
}

let netBalanceMonthPromise: Promise<number> | null = null;
function loadNetBalanceMonth(): Promise<number> {
  netBalanceMonthPromise ??= (async () => {
    const { from, to } = currentMonthRange();
    const report = await getReport({ date_from: from, date_to: to });
    return report.totals.net_cents;
  })();
  return netBalanceMonthPromise;
}

let usersSummaryPromise: Promise<UsersSummary> | null = null;
function loadUsersSummary(): Promise<UsersSummary> {
  usersSummaryPromise ??= getUsersSummary();
  return usersSummaryPromise;
}

// El saldo agregado suma todas las cajas (ver balance_cents en el backend), así que solo hay
// un nombre "de la caja" que mostrar cuando existe exactamente una — con varias, mostrar el
// nombre de una sola sería confuso, así que se omite (null) y el KPI simplemente no pinta esa
// línea.
let primaryCashboxNamePromise: Promise<string | null> | null = null;
function loadPrimaryCashboxName(): Promise<string | null> {
  primaryCashboxNamePromise ??= listCashboxes().then(({ cashboxes }) =>
    cashboxes.length === 1 ? cashboxes[0]!.name : null,
  );
  return primaryCashboxNamePromise;
}

export const kpiDataSources = {
  financeSummary: loadFinanceSummary,
  categoryCount: loadCategoryCount,
  netBalanceMonth: loadNetBalanceMonth,
  usersSummary: loadUsersSummary,
  primaryCashboxName: loadPrimaryCashboxName,
};

// Debe llamarse al empezar cada pase de carga nuevo (lo hace loadKpiProps automáticamente)
// para no servir datos de un pase anterior. Asume una sola página consumiendo KPIs a la vez,
// que es el caso hoy (finance/settings/home son las únicas páginas y nunca están montadas
// dos a la vez) — si en el futuro dos vistas cargan KPIs en paralelo, esto habría que
// convertirlo en una caché por pase en vez de módulo-global.
export function resetKpiDataCache() {
  financeSummaryPromise = null;
  categoryCountPromise = null;
  netBalanceMonthPromise = null;
  usersSummaryPromise = null;
  primaryCashboxNamePromise = null;
}
