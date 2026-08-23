<script setup lang="ts">
import { usePermissionsStore } from "~/core/stores/permissions";
import KpiCard from "~/core/components/ui/KpiCard.vue";
import {
  FinanceBalanceKpi,
  FinanceCashMonthKpi,
  FinanceCardMonthKpi,
  FinanceDraftsKpi,
  FinanceLabelsKpi,
  FinanceReportsKpi,
  loadKpiProps,
} from "~/core/components/kpis";

const { t } = useI18n();
const permissionsStore = usePermissionsStore();

useHead({ title: t("finance.title") });

const loading = ref(true);
const errorMessage = ref("");
const kpiProps = ref<Record<string, Record<string, unknown>>>({});

async function load() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const ids = ["finance_balance", "finance_cash_month", "finance_card_month"];
    if (permissionsStore.has("CASHBOX_MANAGE")) {
      ids.push("finance_drafts", "finance_labels", "finance_reports");
    }
    kpiProps.value = await loadKpiProps(ids);
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
      <KpiCard to="/finance/new" kpi-id="finance_balance">
        <FinanceBalanceKpi :loading="loading" v-bind="kpiProps.finance_balance" />
      </KpiCard>

      <KpiCard to="/finance/transactions?filter=cash" kpi-id="finance_cash_month">
        <FinanceCashMonthKpi :loading="loading" v-bind="kpiProps.finance_cash_month" />
      </KpiCard>

      <KpiCard to="/finance/transactions?filter=card" kpi-id="finance_card_month">
        <FinanceCardMonthKpi :loading="loading" v-bind="kpiProps.finance_card_month" />
      </KpiCard>

      <KpiCard
        v-if="permissionsStore.has('CASHBOX_MANAGE')"
        to="/finance/transactions?filter=review"
        variant="warning"
        kpi-id="finance_drafts"
      >
        <FinanceDraftsKpi :loading="loading" v-bind="kpiProps.finance_drafts" />
      </KpiCard>

      <KpiCard v-if="permissionsStore.has('CASHBOX_MANAGE')" to="/finance/labels" kpi-id="finance_labels">
        <FinanceLabelsKpi :loading="loading" v-bind="kpiProps.finance_labels" />
      </KpiCard>

      <KpiCard v-if="permissionsStore.has('CASHBOX_MANAGE')" to="/finance/reports" kpi-id="finance_reports">
        <FinanceReportsKpi :loading="loading" v-bind="kpiProps.finance_reports" />
      </KpiCard>
    </div>
  </div>
</template>
