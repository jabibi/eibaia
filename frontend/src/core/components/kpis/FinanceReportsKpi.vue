<script setup lang="ts">
import { formatCurrency } from "~/core/utils/currency";

defineProps<{ loading: boolean; netCents?: number | null }>();
const { t } = useI18n();
</script>

<template>
  <p class="text-xs font-medium text-slate-500">{{ t("finance.kpi.reports") }}</p>
  <p class="mt-2 text-2xl font-bold text-slate-900">{{ loading ? "…" : formatCurrency(netCents ?? 0) }}</p>
  <p class="mt-1 text-xs text-slate-500">{{ t("finance.kpi.reportsHint") }}</p>
</template>
