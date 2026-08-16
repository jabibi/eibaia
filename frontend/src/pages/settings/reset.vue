<script setup lang="ts">
import { apiFetch } from "~/core/api/http";
import { useAuthStore } from "~/core/stores/auth";
import { usePermissionsStore } from "~/core/stores/permissions";

const authStore = useAuthStore();
const permissionsStore = usePermissionsStore();
const { t } = useI18n();

if (!permissionsStore.has("SYSTEM_ADMIN")) {
  await navigateTo("/home");
}

const CONFIRM_WORD = "RESTABLECER";

const confirmText = ref("");
const loading = ref(false);
const errorMessage = ref("");

const canSubmit = computed(() => confirmText.value.trim().toUpperCase() === CONFIRM_WORD);

async function handleReset() {
  if (!canSubmit.value) return;

  loading.value = true;
  errorMessage.value = "";
  try {
    await apiFetch("/system/reset", { method: "POST" });
    await authStore.logout();
    await navigateTo("/");
  } catch (error) {
    errorMessage.value = t("settings.reset.error");
    loading.value = false;
  }
}
</script>

<template>
  <div class="max-w-lg">
    <h1 class="text-2xl font-semibold text-slate-800">{{ t("settings.reset.title") }}</h1>

    <div class="mt-4 rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800">
      {{ t("settings.reset.warning") }}
    </div>

    <div class="mt-6">
      <label class="mb-1 block text-sm text-slate-600">
        {{ t("settings.reset.confirmLabel", { word: CONFIRM_WORD }) }}
      </label>
      <input
        v-model="confirmText"
        type="text"
        :placeholder="CONFIRM_WORD"
        class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
      />
    </div>

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <Button
      :label="t('settings.reset.submit')"
      severity="danger"
      class="mt-4"
      :disabled="!canSubmit"
      :loading="loading"
      @click="handleReset"
    />
  </div>
</template>
