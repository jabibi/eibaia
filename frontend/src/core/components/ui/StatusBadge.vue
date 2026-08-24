<script setup lang="ts">
withDefaults(
  defineProps<{ label: string; variant?: "neutral" | "success" | "warning"; icon?: string }>(),
  { variant: "neutral", icon: undefined },
);
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium"
    :class="{
      'bg-slate-100 text-slate-600': variant === 'neutral',
      'bg-emerald-100 text-emerald-700': variant === 'success',
      'bg-amber-100 text-amber-700': variant === 'warning',
    }"
  >
    <Icon v-if="icon" :name="icon" />
    {{ label }}
  </span>
</template>
