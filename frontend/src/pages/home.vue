<script setup lang="ts">
import { useAuthStore } from "~/core/stores/auth";

const authStore = useAuthStore();
const { t } = useI18n();

useHead({ title: t("sidebar.home") });
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">
      {{ t("home.greeting", { name: authStore.user?.displayName ?? "" }) }}
    </h1>
    <p class="mt-2 text-slate-500">{{ t("home.summary") }}</p>
  </div>
</template>
