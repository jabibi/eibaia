<script setup lang="ts">
import GithubLink from "~/core/components/GithubLink.vue";
import { useAuthStore } from "~/core/stores/auth";

definePageMeta({ layout: false });

const authStore = useAuthStore();
const loading = ref(false);
const errorMessage = ref("");

async function handleLogin() {
  loading.value = true;
  errorMessage.value = "";
  try {
    await authStore.loginWithGoogle();
    await navigateTo("/inicio");
  } catch (error) {
    errorMessage.value = "No se ha podido iniciar sesión. Inténtalo de nuevo.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="relative flex min-h-screen flex-col items-center justify-center gap-8 bg-slate-50 px-4">
    <GithubLink class="fixed right-4 top-4" size="h-6 w-6" />

    <img :src="'/img/logo-home.svg'" alt="ElosuE! - Gestión del hogar" />

    <Button
      label="Iniciar sesión con Google"
      icon="pi pi-google"
      :loading="loading"
      @click="handleLogin"
    />

    <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>
  </div>
</template>
