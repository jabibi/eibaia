<script setup lang="ts">
import { useAuthStore } from "~/core/stores/auth";

const authStore = useAuthStore();
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">
      Hola, {{ authStore.user?.displayName ?? "" }}
    </h1>
    <p class="mt-2 text-slate-500">Resumen general del hogar (próximamente).</p>
  </div>
</template>
