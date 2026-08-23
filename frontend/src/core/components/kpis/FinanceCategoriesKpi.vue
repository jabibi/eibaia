<script setup lang="ts">
// `editing` no se usa aquí — solo se declara para que /home pueda pasarlo por igual a
// todos los KPI (ver FinanceBalanceKpi.vue) sin que Vue avise de un atributo no declarado.
defineProps<{ loading: boolean; count?: number | null; editing?: boolean }>();
const { t } = useI18n();
</script>

<template>
  <p class="text-xs font-medium text-slate-500">{{ t("finance.kpi.categories") }}</p>
  <p class="mt-2 text-2xl font-bold text-slate-900">{{ loading ? "…" : (count ?? 0) }}</p>
  <p class="mt-1 text-xs text-slate-500">{{ t("finance.kpi.categoriesHint") }}</p>
</template>
