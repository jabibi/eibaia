<script setup lang="ts">
defineProps<{ label: string }>();
</script>

<template>
  <span class="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
    {{ label }}
  </span>
</template>
