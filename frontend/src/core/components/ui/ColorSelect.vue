<script setup lang="ts">
import { LABEL_COLOR_CLASSES, type LabelColor } from "~/core/ui/labelColors";

interface ColorSelectOption {
  value: string;
  label: string;
  color: LabelColor;
}

const props = defineProps<{ modelValue: string; options: ColorSelectOption[] }>();
defineEmits<{ (e: "update:modelValue", value: string): void }>();

const selectedColor = computed(() => props.options.find((option) => option.value === props.modelValue)?.color ?? null);
</script>

<template>
  <div class="relative">
    <span
      v-if="selectedColor"
      class="pointer-events-none absolute left-2.5 top-1/2 h-2.5 w-2.5 -translate-y-1/2 rounded-full"
      :class="LABEL_COLOR_CLASSES[selectedColor].swatch"
    />
    <select
      :value="modelValue"
      class="w-full rounded-md border border-slate-300 bg-white py-1.5 pr-8 text-xs text-slate-700 shadow-sm transition-colors focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 md:text-sm"
      :class="selectedColor ? 'pl-7' : 'pl-3'"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    >
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
        :class="[LABEL_COLOR_CLASSES[option.color].chipBg, LABEL_COLOR_CLASSES[option.color].text]"
      >
        {{ option.label }}
      </option>
    </select>
  </div>
</template>
