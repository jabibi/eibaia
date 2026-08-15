<script setup lang="ts">
import { listMovements, type Movement } from "~/modules/finance/api";
import MovementList from "~/modules/finance/components/MovementList.vue";

const { t } = useI18n();
const loadedMovements = ref<Movement[]>([]);
const nextPageToken = ref<string | null>(null);
const loading = ref(true);
const errorMessage = ref("");

async function loadFirstPage() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await listMovements(null);
    loadedMovements.value = response.movements;
    nextPageToken.value = response.next_page_token;
  } catch (error) {
    errorMessage.value = t("finance.transactions.loadError");
  } finally {
    loading.value = false;
  }
}

async function loadMore() {
  if (!nextPageToken.value) return;
  loading.value = true;
  try {
    const response = await listMovements(nextPageToken.value);
    loadedMovements.value = [...loadedMovements.value, ...response.movements];
    nextPageToken.value = response.next_page_token;
  } catch (error) {
    errorMessage.value = t("finance.transactions.loadError");
  } finally {
    loading.value = false;
  }
}

onMounted(loadFirstPage);
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

    <h1 class="text-2xl font-semibold text-slate-800">{{ t("finance.transactions.title") }}</h1>

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <MovementList :movements="loadedMovements" :loading="loading" show-actions @refresh="loadFirstPage" />

    <div v-if="nextPageToken" class="mt-4 flex justify-center">
      <Button :label="t('finance.transactions.loadMore')" text @click="loadMore" />
    </div>
  </div>
</template>
