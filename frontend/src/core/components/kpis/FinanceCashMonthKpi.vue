<script setup lang="ts">
import { formatCurrency } from "~/core/utils/currency";
import type { FinanceSummary } from "~/modules/finance/api";

defineProps<{ loading: boolean; summary?: FinanceSummary | null }>();
const { t } = useI18n();
</script>

<template>
  <p class="text-xs font-medium text-slate-500">{{ t("finance.kpi.cashMonth") }}</p>
  <p class="mt-2 text-2xl font-bold text-slate-900">
    {{ loading ? "…" : formatCurrency(summary?.cash_expenses_month.total_cents ?? 0) }}
  </p>
  <p class="mt-1 text-xs text-slate-500">
    {{ t("finance.kpi.movementsCount", { count: summary?.cash_expenses_month.count ?? 0 }) }}
  </p>
</template>
