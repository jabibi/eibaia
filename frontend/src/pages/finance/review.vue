<script setup lang="ts">
import { listMovements, type Movement } from "~/modules/finance/api";
import MovementList from "~/modules/finance/components/MovementList.vue";
import { usePermissionsStore } from "~/core/stores/permissions";

const permissionsStore = usePermissionsStore();
const { t } = useI18n();

if (!permissionsStore.has("CASHBOX_MANAGE")) {
  await navigateTo("/home");
}

useHead({ title: t("finance.review.title") });

const drafts = ref<Movement[]>([]);
const loading = ref(true);
const errorMessage = ref("");

async function load() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await listMovements(null, "draft");
    drafts.value = response.movements;
  } catch (error) {
    errorMessage.value = t("finance.review.loadError");
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">{{ t("finance.review.title") }}</h1>

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <MovementList
      :movements="drafts"
      :loading="loading"
      :empty-message="t('finance.review.empty')"
      show-actions
      @refresh="load"
    />
  </div>
</template>
