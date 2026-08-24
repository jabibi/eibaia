<script setup lang="ts">
withDefaults(defineProps<{ tone?: "neutral" | "warning" }>(), { tone: "neutral" });
</script>

<template>
  <div
    class="rounded-lg border shadow-sm"
    :class="{
      'border-slate-200 bg-white': tone === 'neutral',
      'border-amber-200 bg-amber-50': tone === 'warning',
    }"
  >
    <slot />
  </div>
</template>
