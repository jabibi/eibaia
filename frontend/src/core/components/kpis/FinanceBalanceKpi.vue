<script setup lang="ts">
import { formatCurrency } from "~/core/utils/currency";
import type { FinanceSummary } from "~/modules/finance/api";

// `editing` llega desde /home cuando esta tarjeta se pinta dentro del modo edición del
// dashboard — ahí el botón debe quedar inerte (ninguna tarjeta KPI conserva sus acciones
// habituales en ese modo), pero en el mismo sitio, solo con un tono gris que lo deje claro.
defineProps<{ loading: boolean; summary?: FinanceSummary | null; editing?: boolean }>();
const { t } = useI18n();

function goToNewMovement() {
  navigateTo("/finance/new");
}
</script>

<template>
  <button
    type="button"
    :disabled="editing"
    class="pointer-events-auto absolute right-12 top-1/2 z-10 flex h-12 w-12 -translate-y-1/2 items-center justify-center rounded-full shadow-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 active:scale-95 disabled:cursor-not-allowed disabled:shadow-none disabled:active:scale-100"
    :class="editing ? 'bg-slate-200 text-slate-400' : 'bg-emerald-600 text-white hover:bg-emerald-700'"
    :title="t('finance.addMovement')"
    :aria-label="t('finance.addMovement')"
    @click.stop.prevent="goToNewMovement"
  >
    <Icon name="lucide:plus" class="text-xl" />
  </button>
  <p class="text-xs font-semibold uppercase tracking-wider text-emerald-800/80">{{ t("finance.kpi.balance") }}</p>
  <p class="mt-2 text-2xl font-bold text-emerald-950">
    {{ loading ? "…" : formatCurrency(summary?.balance_cents ?? 0) }}
  </p>
</template>
