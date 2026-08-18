<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: "primary" | "secondary";
    type?: "button" | "submit";
    disabled?: boolean;
  }>(),
  { variant: "primary", type: "button", disabled: false },
);
</script>

<template>
  <button
    :type="type"
    :disabled="disabled"
    class="rounded-md px-3.5 py-1.5 text-xs font-medium transition-colors"
    :class="
      variant === 'primary'
        ? 'bg-indigo-600 text-white shadow-sm hover:bg-indigo-700 disabled:opacity-60'
        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-800'
    "
  >
    <slot />
  </button>
</template>
