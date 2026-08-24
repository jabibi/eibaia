<script setup lang="ts">
import { CATEGORY_COLOR_CLASSES, type CategoryColor } from "~/core/ui/categoryColors";

interface ColorSelectOption {
  value: string;
  label: string;
  color: CategoryColor;
}

const props = defineProps<{ modelValue: string; options: ColorSelectOption[]; id?: string }>();
defineEmits<{ (e: "update:modelValue", value: string): void }>();

const selectedColor = computed(() => props.options.find((option) => option.value === props.modelValue)?.color ?? null);
</script>

<template>
  <div class="relative">
    <span
      v-if="selectedColor"
      class="pointer-events-none absolute left-2.5 top-1/2 h-2.5 w-2.5 -translate-y-1/2 rounded-full"
      :class="CATEGORY_COLOR_CLASSES[selectedColor].swatch"
    />
    <select
      :id="id"
      :value="modelValue"
      class="w-full rounded-md border border-slate-300 bg-white py-1.5 pr-8 text-xs text-slate-700 shadow-sm transition-colors focus:border-green-700 focus:outline-none focus:ring-1 focus:ring-green-700 md:text-sm"
      :class="selectedColor ? 'pl-7' : 'pl-3'"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    >
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
        :class="[CATEGORY_COLOR_CLASSES[option.color].chipBg, CATEGORY_COLOR_CLASSES[option.color].text]"
      >
        {{ option.label }}
      </option>
    </select>
  </div>
</template>
