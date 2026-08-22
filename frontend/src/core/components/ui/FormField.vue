<script setup lang="ts">
defineProps<{ label: string; inputId?: string }>();
</script>

<template>
  <div>
    <label
      class="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-600"
      :for="inputId"
      >{{ label }}</label
    >
    <slot />
  </div>
</template>
