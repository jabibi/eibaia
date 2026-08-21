<script setup lang="ts">
withDefaults(defineProps<{ label: string; variant?: "neutral" | "success" | "warning" }>(), { variant: "neutral" });
</script>

<template>
  <span
    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
    :class="{
      'bg-slate-100 text-slate-600': variant === 'neutral',
      'bg-emerald-100 text-emerald-700': variant === 'success',
      'bg-amber-100 text-amber-700': variant === 'warning',
    }"
  >
    {{ label }}
  </span>
</template>
