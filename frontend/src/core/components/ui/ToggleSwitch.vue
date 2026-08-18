<script setup lang="ts">
defineProps<{ modelValue: boolean }>();
defineEmits<{ (e: "update:modelValue", value: boolean): void }>();
</script>

<template>
  <button
    type="button"
    role="switch"
    :aria-checked="modelValue"
    class="relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1"
    :class="modelValue ? 'bg-indigo-600' : 'bg-slate-300'"
    @click="$emit('update:modelValue', !modelValue)"
  >
    <span
      class="inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform"
      :class="modelValue ? 'translate-x-4' : 'translate-x-1'"
    />
  </button>
</template>
