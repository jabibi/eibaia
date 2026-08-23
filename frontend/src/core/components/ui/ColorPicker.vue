<script setup lang="ts">
import { CATEGORY_COLORS, CATEGORY_COLOR_CLASSES, type CategoryColor } from "~/core/ui/categoryColors";

defineProps<{ modelValue: CategoryColor; ariaLabel?: string }>();
defineEmits<{ (e: "update:modelValue", value: CategoryColor): void }>();

const { t } = useI18n();
</script>

<template>
  <div class="flex flex-wrap gap-2" role="radiogroup" :aria-label="ariaLabel">
    <button
      v-for="color in CATEGORY_COLORS"
      :key="color"
      type="button"
      role="radio"
      :aria-checked="modelValue === color"
      :aria-label="t(`finance.colors.${color}`)"
      :title="t(`finance.colors.${color}`)"
      class="h-7 w-7 rounded-full transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-indigo-500"
      :class="[CATEGORY_COLOR_CLASSES[color].swatch, modelValue === color ? 'ring-2 ring-offset-1 ring-slate-800' : '']"
      @click="$emit('update:modelValue', color)"
    />
  </div>
</template>
