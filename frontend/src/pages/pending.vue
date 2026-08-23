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

// Un admin puede conceder el rol mientras esta pestaña/PWA está abierta en segundo
// plano; onAuthStateChanged no se dispara para eso (no cambia el estado de sesión,
// solo el role_id en Firestore), así que no basta con la comprobación inicial del
// middleware. Al volver a primer plano, se re-consulta el rol y, si ya lo tiene, se
// navega a /home sin que haga falta recargar la página a mano.
async function checkApproval() {
  await authStore.refreshRoleId();
  if (authStore.isApproved) {
    await navigateTo("/home");
  }
}

function handleVisibilityChange() {
  if (document.visibilityState === "visible") {
    checkApproval();
  }
}

onMounted(() => {
  document.addEventListener("visibilitychange", handleVisibilityChange);
});

onUnmounted(() => {
  document.removeEventListener("visibilitychange", handleVisibilityChange);
});
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
