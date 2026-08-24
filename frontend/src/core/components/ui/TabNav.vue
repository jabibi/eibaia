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
        :aria-current="modelValue === option.value ? 'page' : undefined"
        class="border-b-2 px-1 py-3 text-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500"
        :class="
          modelValue === option.value
            ? 'border-sky-600 font-medium text-sky-600'
            : 'border-transparent text-slate-500 hover:text-slate-700'
        "
        @click="$emit('update:modelValue', option.value)"
      >
        {{ option.label }}
      </button>
    </nav>
  </div>
</template>
