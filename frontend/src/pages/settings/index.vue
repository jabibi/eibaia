<script setup lang="ts">
import { getUsersSummary, type UsersSummary } from "~/modules/users/api";
import KpiCard from "~/core/components/ui/KpiCard.vue";

const { t } = useI18n();

useHead({ title: t("settings.title") });

const summary = ref<UsersSummary | null>(null);
const loading = ref(true);
const errorMessage = ref("");

async function load() {
  loading.value = true;
  errorMessage.value = "";
  try {
    summary.value = await getUsersSummary();
  } catch (error) {
    errorMessage.value = t("settings.loadError");
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">{{ t("settings.title") }}</h1>

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <div class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
      <KpiCard to="/settings/users">
        <p class="text-sm text-slate-500">{{ t("settings.cards.users") }}</p>
        <div class="mt-3 flex items-center gap-6">
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ loading ? "…" : summary?.active ?? 0 }}</p>
            <p class="text-xs text-slate-500">{{ t("users.filters.active") }}</p>
          </div>
          <div>
            <p class="text-2xl font-bold text-emerald-600">{{ loading ? "…" : summary?.new ?? 0 }}</p>
            <p class="text-xs text-slate-500">{{ t("users.filters.new") }}</p>
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-500">{{ loading ? "…" : summary?.inactive ?? 0 }}</p>
            <p class="text-xs text-slate-500">{{ t("users.filters.inactive") }}</p>
          </div>
        </div>
      </KpiCard>

      <KpiCard to="/settings/reset" variant="danger">
        <p class="text-sm text-slate-500">{{ t("settings.cards.reset") }}</p>
        <p class="mt-3 text-sm text-red-600">{{ t("settings.cards.resetHint") }}</p>
      </KpiCard>
    </div>
  </div>
</template>
