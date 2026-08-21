<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: "primary" | "secondary" | "danger";
    type?: "button" | "submit";
    disabled?: boolean;
    icon?: string;
    loading?: boolean;
  }>(),
  { variant: "primary", type: "button", disabled: false, icon: undefined, loading: false },
);
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="inline-flex items-center justify-center gap-2 rounded-md px-3.5 py-1.5 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 disabled:opacity-60"
    :class="{
      'bg-indigo-600 text-white shadow-sm hover:bg-indigo-700': variant === 'primary',
      'text-slate-600 hover:bg-slate-100 hover:text-slate-800': variant === 'secondary',
      'bg-red-600 text-white shadow-sm hover:bg-red-700': variant === 'danger',
    }"
  >
    <Icon v-if="loading" name="lucide:loader-circle" class="animate-spin" />
    <Icon v-else-if="icon" :name="icon" />
    <slot />
  </button>
</template>
