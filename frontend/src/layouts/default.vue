<script setup lang="ts">
import AppSidebar from "~/core/components/AppSidebar.vue";
import { useSidebar } from "~/core/composables/useSidebar";

const sidebar = useSidebar();

function handleMainClick() {
  sidebar.collapse();
}
</script>

<template>
  <div class="flex h-svh overflow-hidden bg-slate-50">
    <AppSidebar />
    <main class="h-svh flex-1 overflow-y-auto p-6 pt-20 md:pt-6" @click="handleMainClick">
      <slot />
    </main>
  </div>
</template>
