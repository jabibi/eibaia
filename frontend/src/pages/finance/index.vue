<script setup lang="ts">
import { getSummary, type FinanceSummary } from "~/modules/finance/api";
import { formatCurrency } from "~/core/utils/currency";
import { useAuthStore } from "~/core/stores/auth";

const { t } = useI18n();
const authStore = useAuthStore();

const summary = ref<FinanceSummary | null>(null);
const loading = ref(true);
const errorMessage = ref("");

async function load() {
  loading.value = true;
  errorMessage.value = "";
  try {
    summary.value = await getSummary();
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
      <NuxtLink
        to="/finance/new"
        class="group relative rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition hover:border-emerald-300 hover:shadow-md"
      >
        <span
          class="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full bg-emerald-50 text-emerald-600 transition group-hover:bg-emerald-100"
        >
          <i class="pi pi-plus" />
        </span>
        <p class="text-sm text-slate-500">{{ t("finance.kpi.balance") }}</p>
        <p class="mt-2 text-3xl font-bold text-slate-800">
          {{ loading ? "…" : formatCurrency(summary?.balance_cents ?? 0) }}
        </p>
      </NuxtLink>

      <NuxtLink
        to="/finance/transactions?scope=cash"
        class="rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition hover:border-emerald-300 hover:shadow-md"
      >
        <p class="text-sm text-slate-500">{{ t("finance.kpi.cashMonth") }}</p>
        <p class="mt-2 text-2xl font-semibold text-slate-800">
          {{ loading ? "…" : formatCurrency(summary?.cash_expenses_month.total_cents ?? 0) }}
        </p>
        <p class="mt-1 text-xs text-slate-400">
          {{ t("finance.kpi.movementsCount", { count: summary?.cash_expenses_month.count ?? 0 }) }}
        </p>
      </NuxtLink>

      <NuxtLink
        to="/finance/transactions?scope=card"
        class="rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition hover:border-emerald-300 hover:shadow-md"
      >
        <p class="text-sm text-slate-500">{{ t("finance.kpi.cardMonth") }}</p>
        <p class="mt-2 text-2xl font-semibold text-slate-800">
          {{ loading ? "…" : formatCurrency(summary?.card_expenses_month.total_cents ?? 0) }}
        </p>
        <p class="mt-1 text-xs text-slate-400">
          {{ t("finance.kpi.movementsCount", { count: summary?.card_expenses_month.count ?? 0 }) }}
        </p>
        <p class="mt-2 flex items-center gap-1 text-xs text-slate-400">
          <i class="pi pi-info-circle" />
          {{ t("finance.kpi.cardNote") }}
        </p>
      </NuxtLink>

      <NuxtLink
        v-if="authStore.isManager"
        to="/finance/review"
        class="rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition hover:border-amber-300 hover:shadow-md"
      >
        <p class="text-sm text-slate-500">{{ t("finance.kpi.drafts") }}</p>
        <p
          class="mt-2 text-3xl font-bold"
          :class="(summary?.pending_drafts_count ?? 0) > 0 ? 'text-amber-600' : 'text-slate-800'"
        >
          {{ loading ? "…" : (summary?.pending_drafts_count ?? 0) }}
        </p>
        <p class="mt-1 text-xs text-slate-400">{{ t("finance.kpi.draftsHint") }}</p>
      </NuxtLink>
    </div>
  </div>
</template>
