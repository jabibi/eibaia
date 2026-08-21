<script setup lang="ts">
import {
  listLabels,
  listMovements,
  type Label,
  type Movement,
  type MovementStatus,
  type PaymentMethod,
} from "~/modules/finance/api";
import MovementList from "~/modules/finance/components/MovementList.vue";
import Button from "~/core/components/ui/Button.vue";
import TabNav from "~/core/components/ui/TabNav.vue";
import { usePermissionsStore } from "~/core/stores/permissions";

type MovementFilter = "all" | "cash" | "card" | "review";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const permissionsStore = usePermissionsStore();

const filter = computed<string>({
  get() {
    const raw = route.query.filter;
    if (raw === "review" && !permissionsStore.has("CASHBOX_MANAGE")) return "all";
    if (raw === "cash" || raw === "card" || raw === "review") return raw;
    return "all";
  },
  set(value) {
    router.replace({ query: { ...route.query, filter: value === "all" ? undefined : value } });
  },
});

const filterOptions = computed(() => {
  const options = [
    { label: t("finance.transactions.filters.all"), value: "all" },
    { label: t("finance.transactions.filters.cash"), value: "cash" },
    { label: t("finance.transactions.filters.card"), value: "card" },
  ];
  if (permissionsStore.has("CASHBOX_MANAGE")) {
    options.push({ label: t("finance.transactions.filters.review"), value: "review" });
  }
  return options;
});

const pageTitle = computed(() => {
  switch (filter.value as MovementFilter) {
    case "cash":
      return t("finance.transactions.titleCash");
    case "card":
      return t("finance.transactions.titleCard");
    case "review":
      return t("finance.review.title");
    default:
      return t("finance.transactions.title");
  }
});

const addLink = computed(() => (filter.value === "card" ? "/finance/new?type=card" : "/finance/new"));
const showAddButton = computed(() => filter.value !== "review");
const emptyMessage = computed(() => (filter.value === "review" ? t("finance.review.empty") : undefined));

useHead({ title: pageTitle });

const loadedMovements = ref<Movement[]>([]);
const labels = ref<Label[]>([]);
const nextPageToken = ref<string | null>(null);
const loading = ref(true);
const errorMessage = ref("");

async function loadLabels() {
  const response = await listLabels();
  labels.value = response.labels;
}

function listParams(): { status?: MovementStatus; scope?: PaymentMethod } {
  if (filter.value === "review") return { status: "draft" };
  if (filter.value === "cash" || filter.value === "card") return { scope: filter.value as PaymentMethod };
  return {};
}

async function loadFirstPage() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const { status, scope } = listParams();
    const response = await listMovements(null, status, scope);
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
    const { status, scope } = listParams();
    const response = await listMovements(nextPageToken.value, status, scope);
    loadedMovements.value = [...loadedMovements.value, ...response.movements];
    nextPageToken.value = response.next_page_token;
  } catch (error) {
    errorMessage.value = t("finance.transactions.loadError");
  } finally {
    loading.value = false;
  }
}

watch(filter, loadFirstPage);
onMounted(() => {
  loadFirstPage();
  loadLabels();
});
</script>

<template>
  <div class="relative">
    <NuxtLink
      v-if="showAddButton"
      :to="addLink"
      class="fixed right-6 top-6 z-10 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-600 text-white shadow-lg hover:bg-emerald-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-emerald-500"
      :aria-label="t('finance.addMovement')"
    >
      <Icon name="lucide:plus" class="text-xl" />
    </NuxtLink>

    <h1 class="text-2xl font-semibold text-slate-800">{{ pageTitle }}</h1>

    <TabNav v-model="filter" :options="filterOptions" class="mt-6" />

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <MovementList
      :movements="loadedMovements"
      :labels="labels"
      :loading="loading"
      :empty-message="emptyMessage"
      show-actions
      @refresh="loadFirstPage"
    />

    <div v-if="nextPageToken" class="mt-4 flex justify-center">
      <Button variant="secondary" @click="loadMore">{{ t("finance.transactions.loadMore") }}</Button>
    </div>
  </div>
</template>
