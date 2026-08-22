<script setup lang="ts">
import { getReport, getSummary, listLabels, type FinanceSummary } from "~/modules/finance/api";
import { formatCurrency } from "~/core/utils/currency";
import { currentMonthRange } from "~/core/utils/dateRange";
import { usePermissionsStore } from "~/core/stores/permissions";
import KpiCard from "~/core/components/ui/KpiCard.vue";

const { t } = useI18n();
const permissionsStore = usePermissionsStore();

useHead({ title: t("finance.title") });

const summary = ref<FinanceSummary | null>(null);
const labelCount = ref<number | null>(null);
const netBalanceMonth = ref<number | null>(null);
const loading = ref(true);
const errorMessage = ref("");

async function load() {
  loading.value = true;
  errorMessage.value = "";
  try {
    summary.value = await getSummary();
    if (permissionsStore.has("CASHBOX_MANAGE")) {
      const { labels } = await listLabels();
      labelCount.value = labels.length;

      const { from, to } = currentMonthRange();
      const report = await getReport({ date_from: from, date_to: to });
      netBalanceMonth.value = report.totals.net_cents;
    }
  } catch (error) {
    errorMessage.value = t("finance.loadError");
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">{{ t("finance.title") }}</h1>

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <div class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <KpiCard to="/finance/new">
        <span
          class="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full bg-emerald-50 text-emerald-600 transition group-hover:bg-emerald-100"
        >
          <Icon name="lucide:plus" />
        </span>
        <p class="text-sm text-slate-500">{{ t("finance.kpi.balance") }}</p>
        <p class="mt-2 text-3xl font-bold text-slate-800">
          {{ loading ? "…" : formatCurrency(summary?.balance_cents ?? 0) }}
        </p>
      </KpiCard>

      <KpiCard to="/finance/transactions?filter=cash">
        <p class="text-sm text-slate-500">{{ t("finance.kpi.cashMonth") }}</p>
        <p class="mt-2 text-2xl font-semibold text-slate-800">
          {{ loading ? "…" : formatCurrency(summary?.cash_expenses_month.total_cents ?? 0) }}
        </p>
        <p class="mt-1 text-xs text-slate-500">
          {{ t("finance.kpi.movementsCount", { count: summary?.cash_expenses_month.count ?? 0 }) }}
        </p>
      </KpiCard>

      <KpiCard to="/finance/transactions?filter=card">
        <p class="text-sm text-slate-500">{{ t("finance.kpi.cardMonth") }}</p>
        <p class="mt-2 text-2xl font-semibold text-slate-800">
          {{ loading ? "…" : formatCurrency(summary?.card_expenses_month.total_cents ?? 0) }}
        </p>
        <p class="mt-1 text-xs text-slate-500">
          {{ t("finance.kpi.movementsCount", { count: summary?.card_expenses_month.count ?? 0 }) }}
        </p>
        <p class="mt-2 flex items-center gap-1 text-xs text-slate-500">
          <Icon name="lucide:info" />
          {{ t("finance.kpi.cardNote") }}
        </p>
      </KpiCard>

      <KpiCard v-if="permissionsStore.has('CASHBOX_MANAGE')" to="/finance/transactions?filter=review" variant="warning">
        <p class="text-sm text-slate-500">{{ t("finance.kpi.drafts") }}</p>
        <p
          class="mt-2 text-3xl font-bold"
          :class="(summary?.pending_drafts_count ?? 0) > 0 ? 'text-amber-600' : 'text-slate-800'"
        >
          {{ loading ? "…" : (summary?.pending_drafts_count ?? 0) }}
        </p>
        <p class="mt-1 text-xs text-slate-500">{{ t("finance.kpi.draftsHint") }}</p>
      </KpiCard>

      <KpiCard v-if="permissionsStore.has('CASHBOX_MANAGE')" to="/finance/labels">
        <p class="text-sm text-slate-500">{{ t("finance.kpi.labels") }}</p>
        <p class="mt-2 text-3xl font-bold text-slate-800">
          {{ loading ? "…" : (labelCount ?? 0) }}
        </p>
        <p class="mt-1 text-xs text-slate-500">{{ t("finance.kpi.labelsHint") }}</p>
      </KpiCard>

      <KpiCard v-if="permissionsStore.has('CASHBOX_MANAGE')" to="/finance/reports">
        <p class="text-sm text-slate-500">{{ t("finance.kpi.reports") }}</p>
        <p class="mt-2 text-2xl font-semibold text-slate-800">
          {{ loading ? "…" : formatCurrency(netBalanceMonth ?? 0) }}
        </p>
        <p class="mt-1 text-xs text-slate-500">{{ t("finance.kpi.reportsHint") }}</p>
      </KpiCard>
    </div>
  </div>
</template>
