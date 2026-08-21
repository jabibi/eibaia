<script setup lang="ts">
import Logo from "~/core/components/Logo.vue";
import Button from "~/core/components/ui/Button.vue";
import GithubLink from "~/core/components/GithubLink.vue";
import { useAuthStore } from "~/core/stores/auth";

definePageMeta({ layout: false });

const authStore = useAuthStore();
const { t } = useI18n();

useHead({ title: t("pending.title") });

async function handleLogout() {
  await authStore.logout();
  await navigateTo("/");
}
</script>

<template>
  <div class="relative flex min-h-svh flex-col items-center justify-center gap-8 bg-slate-50 px-4">
    <GithubLink class="fixed right-4 top-4" size="text-xl" />

    <h1 class="sr-only">{{ t("pending.title") }}</h1>
    <Logo />

    <p class="max-w-sm text-center text-slate-600">{{ t("pending.message") }}</p>

    <Button variant="danger" icon="lucide:log-out" @click="handleLogout">
      {{ t("pending.logout") }}
    </Button>
  </div>
</template>
