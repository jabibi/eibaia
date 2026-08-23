<script setup lang="ts">
import { formatCurrency } from "~/core/utils/currency";
import type { FinanceSummary } from "~/modules/finance/api";

defineProps<{ loading: boolean; summary?: FinanceSummary | null }>();
const { t } = useI18n();
</script>

<template>
  <span
    class="absolute right-12 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-emerald-50 text-emerald-600 transition group-hover:bg-emerald-100"
  >
    <Icon name="lucide:plus" />
  </span>
  <p class="text-sm text-slate-500">{{ t("finance.kpi.balance") }}</p>
  <p class="mt-2 text-3xl font-bold text-slate-800">
    {{ loading ? "…" : formatCurrency(summary?.balance_cents ?? 0) }}
  </p>
</template>
