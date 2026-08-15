<script setup lang="ts">
import AppLogo from "~/core/components/AppLogo.vue";
import GithubLink from "~/core/components/GithubLink.vue";
import { useAuthStore } from "~/core/stores/auth";

definePageMeta({ layout: false });

const authStore = useAuthStore();
const { t } = useI18n();

async function handleLogout() {
  await authStore.logout();
  await navigateTo("/");
}
</script>

<template>
  <div class="relative flex min-h-svh flex-col items-center justify-center gap-8 bg-slate-50 px-4">
    <GithubLink class="fixed right-4 top-4" size="h-6 w-6" />

    <AppLogo />

    <p class="max-w-sm text-center text-slate-600">{{ t("pending.message") }}</p>

    <Button :label="t('pending.logout')" icon="pi pi-sign-out" severity="secondary" @click="handleLogout" />
  </div>
</template>
