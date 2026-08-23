<script setup lang="ts">
import type { FinanceSummary } from "~/modules/finance/api";

// `editing` no se usa aquí — solo se declara para que /home pueda pasarlo por igual a
// todos los KPI (ver FinanceBalanceKpi.vue) sin que Vue avise de un atributo no declarado.
defineProps<{ loading: boolean; summary?: FinanceSummary | null; editing?: boolean }>();
const { t } = useI18n();
</script>

<template>
  <p class="text-xs font-medium text-slate-500">{{ t("finance.kpi.drafts") }}</p>
  <p
    class="mt-2 text-2xl font-bold"
    :class="(summary?.pending_drafts_count ?? 0) > 0 ? 'text-amber-600' : 'text-slate-900'"
  >
    {{ loading ? "…" : (summary?.pending_drafts_count ?? 0) }}
  </p>
  <p class="mt-1 text-xs text-slate-500">{{ t("finance.kpi.draftsHint") }}</p>
</template>
