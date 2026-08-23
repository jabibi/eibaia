<script setup lang="ts">
import KpiCard from "~/core/components/ui/KpiCard.vue";
import { SettingsUsersKpi, SettingsResetKpi, loadKpiProps } from "~/core/components/kpis";

const { t } = useI18n();

useHead({ title: t("settings.title") });

const loading = ref(true);
const errorMessage = ref("");
const kpiProps = ref<Record<string, Record<string, unknown>>>({});

async function load() {
  loading.value = true;
  errorMessage.value = "";
  try {
    kpiProps.value = await loadKpiProps(["settings_users", "settings_reset"]);
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
      <KpiCard to="/settings/users" kpi-id="settings_users">
        <SettingsUsersKpi :loading="loading" v-bind="kpiProps.settings_users" />
      </KpiCard>

      <KpiCard to="/settings/reset" variant="danger" kpi-id="settings_reset">
        <SettingsResetKpi v-bind="kpiProps.settings_reset" />
      </KpiCard>
    </div>
  </div>
</template>
