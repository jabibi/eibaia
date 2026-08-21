<script setup lang="ts">
import Logo from "~/core/components/Logo.vue";
import Button from "~/core/components/ui/Button.vue";
import GithubLink from "~/core/components/GithubLink.vue";
import { useAuthStore } from "~/core/stores/auth";

definePageMeta({ layout: false });

const authStore = useAuthStore();
const { t } = useI18n();
const loading = ref(false);
const errorMessage = ref("");

useHead({ title: t("login.title") });

async function handleLogin() {
  loading.value = true;
  errorMessage.value = "";
  try {
    await authStore.loginWithGoogle();
    await navigateTo("/home");
  } catch (error) {
    errorMessage.value = t("login.loginError");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="relative flex min-h-svh flex-col items-center justify-center gap-8 bg-slate-50 px-4">
    <GithubLink class="fixed right-4 top-4" size="text-xl" />

    <h1 class="sr-only">{{ t("app.title") }}</h1>
    <Logo />

    <Button icon="logos:google-icon" :loading="loading" @click="handleLogin">
      {{ t("login.loginWithGoogle") }}
    </Button>

    <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>
  </div>
</template>
