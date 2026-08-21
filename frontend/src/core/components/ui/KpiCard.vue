<script setup lang="ts">
withDefaults(defineProps<{ to: string; variant?: "default" | "warning" | "danger" }>(), { variant: "default" });
</script>

<template>
  <NuxtLink
    :to="to"
    class="group relative block rounded-lg border bg-white p-6 shadow-sm transition hover:shadow-md focus-visible:outline-none focus-visible:ring-2"
    :class="{
      'border-slate-200 hover:border-emerald-300 focus-visible:ring-indigo-500': variant === 'default',
      'border-slate-200 hover:border-amber-300 focus-visible:ring-indigo-500': variant === 'warning',
      'border-red-200 hover:border-red-300 focus-visible:ring-red-500': variant === 'danger',
    }"
  >
    <slot />
  </NuxtLink>
</template>
