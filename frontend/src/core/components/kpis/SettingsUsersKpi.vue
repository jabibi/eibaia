<script setup lang="ts">
import type { UsersSummary } from "~/modules/users/api";

// `editing` no se usa aquí — solo se declara para que /home pueda pasarlo por igual a
// todos los KPI (ver FinanceBalanceKpi.vue) sin que Vue avise de un atributo no declarado.
defineProps<{ loading: boolean; summary?: UsersSummary | null; editing?: boolean }>();
const { t } = useI18n();
</script>

<template>
  <p class="text-xs font-medium text-slate-500">{{ t("settings.cards.users") }}</p>
  <div class="mt-3 flex items-center gap-6">
    <div>
      <p class="text-2xl font-bold text-slate-900">{{ loading ? "…" : (summary?.active ?? 0) }}</p>
      <p class="text-xs text-slate-500">{{ t("users.filters.active") }}</p>
    </div>
    <div>
      <p class="text-2xl font-bold text-emerald-600">{{ loading ? "…" : (summary?.new ?? 0) }}</p>
      <p class="text-xs text-slate-500">{{ t("users.filters.new") }}</p>
    </div>
    <div>
      <p class="text-2xl font-bold text-slate-500">{{ loading ? "…" : (summary?.inactive ?? 0) }}</p>
      <p class="text-xs text-slate-500">{{ t("users.filters.inactive") }}</p>
    </div>
  </div>
</template>
