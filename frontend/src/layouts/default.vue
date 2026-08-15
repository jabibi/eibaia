<script setup lang="ts">
import AppSidebar from "~/core/components/AppSidebar.vue";
</script>

<template>
  <div class="flex bg-slate-50">
    <AppSidebar />
    <main class="min-h-screen flex-1 overflow-y-auto p-6">
      <slot />
    </main>
  </div>
</template>
