<script setup lang="ts">
defineProps<{ modelValue: string; options: { label: string; value: string }[] }>();
defineEmits<{ (e: "update:modelValue", value: string): void }>();
</script>

<template>
  <div class="border-b border-slate-200">
    <nav class="-mb-px flex gap-6">
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        class="border-b-2 px-1 py-3 text-sm transition"
        :class="
          modelValue === option.value
            ? 'border-indigo-600 font-medium text-indigo-600'
            : 'border-transparent text-slate-500 hover:text-slate-700'
        "
        @click="$emit('update:modelValue', option.value)"
      >
        {{ option.label }}
      </button>
    </nav>
  </div>
</template>
