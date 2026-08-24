<script setup lang="ts">
defineProps<{ modelValue: string }>();
defineEmits<{ (e: "update:modelValue", value: string): void }>();
</script>

<template>
  <input
    :value="modelValue"
    class="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-700 shadow-sm transition-colors focus:border-green-700 focus:outline-none focus:ring-1 focus:ring-green-700 md:text-sm"
    @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
</template>
