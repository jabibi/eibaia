<script setup lang="ts">
defineProps<{ modelValue: string }>();
defineEmits<{ (e: "update:modelValue", value: string): void }>();
</script>

<template>
  <select
    :value="modelValue"
    class="rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs text-slate-700 shadow-sm transition-colors focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
    @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
  >
    <slot />
  </select>
</template>
