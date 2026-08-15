<script setup lang="ts">
import { getBalance, getRecentMovements, type Movement } from "~/modules/finance/api";
import MovementList from "~/modules/finance/components/MovementList.vue";
import { formatCurrency } from "~/core/utils/currency";

const { t } = useI18n();
const balanceCents = ref(0);
const recentMovements = ref<Movement[]>([]);
const loading = ref(true);
const errorMessage = ref("");

async function load() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const [balance, recent] = await Promise.all([getBalance(), getRecentMovements(10)]);
    balanceCents.value = balance.balance_cents;
    recentMovements.value = recent;
  } catch (error) {
    errorMessage.value = t("finance.loadError");
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div class="relative">
    <NuxtLink
      to="/finance/new"
      class="fixed right-6 top-6 z-10 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-600 text-white shadow-lg hover:bg-emerald-700"
      :aria-label="t('finance.addMovement')"
    >
      <i class="pi pi-plus text-xl" />
    </NuxtLink>

    <h1 class="text-2xl font-semibold text-slate-800">{{ t("finance.title") }}</h1>

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <div class="mt-4 rounded-lg border border-slate-200 bg-white p-6">
      <p class="text-sm text-slate-500">{{ t("finance.balance") }}</p>
      <p class="mt-1 text-3xl font-semibold text-slate-800">{{ formatCurrency(balanceCents) }}</p>
    </div>

    <h2 class="mt-8 text-lg font-semibold text-slate-800">{{ t("finance.recentMovements") }}</h2>

    <MovementList :movements="recentMovements" :loading="loading" />
  </div>
</template>
