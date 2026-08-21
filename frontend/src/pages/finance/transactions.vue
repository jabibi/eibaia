<script setup lang="ts">
import { listMovements, type Movement } from "~/modules/finance/api";
import MovementList from "~/modules/finance/components/MovementList.vue";
import Button from "~/core/components/ui/Button.vue";

const { t } = useI18n();
const route = useRoute();

const scope = computed(() => (route.query.scope === "card" ? "card" : "cash") as "cash" | "card");
const pageTitle = computed(() =>
  scope.value === "card" ? t("finance.transactions.titleCard") : t("finance.transactions.titleCash"),
);
const addLink = computed(() => (scope.value === "card" ? "/finance/new?type=card" : "/finance/new"));

useHead({ title: pageTitle });

const loadedMovements = ref<Movement[]>([]);
const nextPageToken = ref<string | null>(null);
const loading = ref(true);
const errorMessage = ref("");

async function loadFirstPage() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await listMovements(null, undefined, scope.value);
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
    const response = await listMovements(nextPageToken.value, undefined, scope.value);
    loadedMovements.value = [...loadedMovements.value, ...response.movements];
    nextPageToken.value = response.next_page_token;
  } catch (error) {
    errorMessage.value = t("finance.transactions.loadError");
  } finally {
    loading.value = false;
  }
}

watch(scope, loadFirstPage);
onMounted(loadFirstPage);
</script>

<template>
  <div class="relative">
    <NuxtLink
      :to="addLink"
      class="fixed right-6 top-6 z-10 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-600 text-white shadow-lg hover:bg-emerald-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-emerald-500"
      :aria-label="t('finance.addMovement')"
    >
      <Icon name="lucide:plus" class="text-xl" />
    </NuxtLink>

    <h1 class="text-2xl font-semibold text-slate-800">{{ pageTitle }}</h1>

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <MovementList :movements="loadedMovements" :loading="loading" show-actions @refresh="loadFirstPage" />

    <div v-if="nextPageToken" class="mt-4 flex justify-center">
      <Button variant="secondary" @click="loadMore">{{ t("finance.transactions.loadMore") }}</Button>
    </div>
  </div>
</template>
