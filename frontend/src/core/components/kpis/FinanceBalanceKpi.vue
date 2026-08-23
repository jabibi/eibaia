<script setup lang="ts">
import { formatCurrency } from "~/core/utils/currency";
import type { FinanceSummary } from "~/modules/finance/api";

defineProps<{ loading: boolean; summary?: FinanceSummary | null; cashboxName?: string | null }>();
const { t } = useI18n();

function goToNewMovement() {
  navigateTo("/finance/new");
}
</script>

<template>
  <button
    type="button"
    class="pointer-events-auto absolute right-12 top-3 z-10 flex h-9 w-9 items-center justify-center rounded-full bg-emerald-600 text-white shadow-sm transition hover:bg-emerald-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 active:scale-95"
    :title="t('finance.addMovement')"
    :aria-label="t('finance.addMovement')"
    @click.stop.prevent="goToNewMovement"
  >
    <Icon name="lucide:plus" class="h-5 w-5" />
  </button>
  <p class="text-xs font-semibold uppercase tracking-wider text-emerald-800/80">{{ t("finance.kpi.balance") }}</p>
  <p v-if="!loading && cashboxName" class="truncate text-sm font-medium text-emerald-900">{{ cashboxName }}</p>
  <p class="mt-2 text-2xl font-bold text-emerald-950">
    {{ loading ? "…" : formatCurrency(summary?.balance_cents ?? 0) }}
  </p>
</template>
