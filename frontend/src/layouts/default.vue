<script setup lang="ts">
import Sidebar from "~/core/components/Sidebar.vue";
</script>

<template>
  <div class="flex h-svh overflow-hidden bg-slate-50">
    <Sidebar />
    <main class="h-svh flex-1 overflow-y-auto p-6 pt-20 md:pt-6">
      <slot />
    </main>
  </div>
</template>
