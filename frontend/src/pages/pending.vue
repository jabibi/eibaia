<script setup lang="ts">
import Logo from "~/core/components/Logo.vue";
import Card from "~/core/components/ui/Card.vue";
import StatusBadge from "~/core/components/ui/StatusBadge.vue";
import Button from "~/core/components/ui/Button.vue";
import GithubLink from "~/core/components/GithubLink.vue";
import { useAuthStore } from "~/core/stores/auth";

definePageMeta({ layout: false });

const authStore = useAuthStore();
const { t } = useI18n();

useHead({ title: t("pending.title") });

const checking = ref(false);
const stillPending = ref(false);

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

async function handleCheckStatus() {
  checking.value = true;
  stillPending.value = false;
  try {
    await checkApproval();
    stillPending.value = !authStore.isApproved;
  } finally {
    checking.value = false;
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
  <div class="relative flex min-h-dvh flex-col items-center justify-center gap-8 bg-slate-50 px-4 py-8">
    <GithubLink class="fixed right-6 top-6 p-2" size="text-xl" />

    <h1 class="sr-only">{{ t("pending.title") }}</h1>
    <Logo />

    <Card tone="warning" class="w-full max-w-sm space-y-4 p-6 text-center">
      <StatusBadge :label="t('pending.status')" icon="lucide:clock" variant="warning" />

      <p class="text-sm text-slate-600">{{ t("pending.message") }}</p>

      <div class="flex flex-col gap-2 pt-2">
        <Button variant="success" icon="lucide:refresh-cw" :loading="checking" @click="handleCheckStatus">
          {{ t("pending.checkStatus") }}
        </Button>
        <Button variant="outline" icon="lucide:log-out" @click="handleLogout">
          {{ t("pending.logout") }}
        </Button>
      </div>

      <p v-if="stillPending" class="text-xs text-amber-950">{{ t("pending.stillPending") }}</p>
    </Card>
  </div>
</template>
