import type { Component } from "vue";
import FinanceBalanceKpi from "./FinanceBalanceKpi.vue";
import FinanceCashMonthKpi from "./FinanceCashMonthKpi.vue";
import FinanceCardMonthKpi from "./FinanceCardMonthKpi.vue";
import FinanceDraftsKpi from "./FinanceDraftsKpi.vue";
import FinanceCategoriesKpi from "./FinanceCategoriesKpi.vue";
import FinanceReportsKpi from "./FinanceReportsKpi.vue";
import SettingsUsersKpi from "./SettingsUsersKpi.vue";
import SettingsResetKpi from "./SettingsResetKpi.vue";
import { kpiDataSources, resetKpiDataCache } from "./dataSources";

export interface KpiEntry {
  component: Component;
  // Cada KPI sabe por sí mismo qué necesita y de dónde lo saca — un consumidor (cualquier
  // página) solo necesita el id, nunca esta lógica.
  loadProps: () => Promise<Record<string, unknown>>;
}

// Una entrada por KPI del registro (ver core/config/kpis.ts): su componente de apariencia y
// cómo cargar sus propios datos. Única fuente de verdad, para que ninguna página necesite
// saber qué API hay detrás de un KPI — solo pide su id.
export const KPI_COMPONENTS: Record<string, KpiEntry> = {
  finance_balance: {
    component: FinanceBalanceKpi,
    loadProps: async () => {
      const [summary, cashboxName] = await Promise.all([
        kpiDataSources.financeSummary(),
        kpiDataSources.primaryCashboxName(),
      ]);
      return { summary, cashboxName };
    },
  },
  finance_cash_month: {
    component: FinanceCashMonthKpi,
    loadProps: async () => ({ summary: await kpiDataSources.financeSummary() }),
  },
  finance_card_month: {
    component: FinanceCardMonthKpi,
    loadProps: async () => ({ summary: await kpiDataSources.financeSummary() }),
  },
  finance_drafts: {
    component: FinanceDraftsKpi,
    loadProps: async () => ({ summary: await kpiDataSources.financeSummary() }),
  },
  finance_categories: {
    component: FinanceCategoriesKpi,
    loadProps: async () => ({ count: await kpiDataSources.categoryCount() }),
  },
  finance_reports: {
    component: FinanceReportsKpi,
    loadProps: async () => ({ netCents: await kpiDataSources.netBalanceMonth() }),
  },
  settings_users: {
    component: SettingsUsersKpi,
    loadProps: async () => ({ summary: await kpiDataSources.usersSummary() }),
  },
  settings_reset: {
    component: SettingsResetKpi,
    loadProps: async () => ({}),
  },
};

// Punto único de entrada para cargar KPIs: dado un listado de ids, carga (desduplicando los
// recursos compartidos) los datos de cada uno y devuelve sus props ya listas para v-bind.
// Cualquier página que pinte KPIs pasa por aquí en vez de reimplementar su propio fetch —
// tanto si la lista de ids es fija (finance/settings) como si la elige el usuario (/home).
export async function loadKpiProps(ids: string[]): Promise<Record<string, Record<string, unknown>>> {
  resetKpiDataCache();
  const entries = await Promise.all(
    ids.map(async (id): Promise<[string, Record<string, unknown>] | null> => {
      const entry = KPI_COMPONENTS[id];
      if (!entry) return null;
      return [id, await entry.loadProps()];
    }),
  );
  return Object.fromEntries(entries.filter((entry): entry is [string, Record<string, unknown>] => entry !== null));
}

export {
  FinanceBalanceKpi,
  FinanceCashMonthKpi,
  FinanceCardMonthKpi,
  FinanceDraftsKpi,
  FinanceCategoriesKpi,
  FinanceReportsKpi,
  SettingsUsersKpi,
  SettingsResetKpi,
};
