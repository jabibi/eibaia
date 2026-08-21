<script setup lang="ts">
import { apiFetch } from "~/core/api/http";
import { useAuthStore } from "~/core/stores/auth";
import { usePermissionsStore } from "~/core/stores/permissions";
import Button from "~/core/components/ui/Button.vue";

const authStore = useAuthStore();
const permissionsStore = usePermissionsStore();
const { t } = useI18n();

if (!permissionsStore.has("SYSTEM_ADMIN")) {
  await navigateTo("/home");
}

useHead({ title: t("settings.reset.title") });

const confirmWord = computed(() => t("settings.reset.confirmWord"));

const confirmText = ref("");
const loading = ref(false);
const errorMessage = ref("");

const canSubmit = computed(() => confirmText.value.trim().toUpperCase() === confirmWord.value);

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
        {{ t("settings.reset.confirmLabel", { word: confirmWord }) }}
      </label>
      <input
        v-model="confirmText"
        type="text"
        :placeholder="confirmWord"
        class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
      />
    </div>

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <Button variant="danger" class="mt-4" :disabled="!canSubmit" :loading="loading" @click="handleReset">
      {{ t("settings.reset.submit") }}
    </Button>
  </div>
</template>
