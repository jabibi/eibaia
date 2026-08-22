<script setup lang="ts">
import { LABEL_COLORS, LABEL_COLOR_CLASSES, type LabelColor } from "~/core/ui/labelColors";

defineProps<{ modelValue: LabelColor; ariaLabel?: string }>();
defineEmits<{ (e: "update:modelValue", value: LabelColor): void }>();

const { t } = useI18n();
</script>

<template>
  <div class="flex flex-wrap gap-2" role="radiogroup" :aria-label="ariaLabel">
    <button
      v-for="color in LABEL_COLORS"
      :key="color"
      type="button"
      role="radio"
      :aria-checked="modelValue === color"
      :aria-label="t(`finance.colors.${color}`)"
      :title="t(`finance.colors.${color}`)"
      class="h-7 w-7 rounded-full transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-indigo-500"
      :class="[LABEL_COLOR_CLASSES[color].swatch, modelValue === color ? 'ring-2 ring-offset-1 ring-slate-800' : '']"
      @click="$emit('update:modelValue', color)"
    />
  </div>
</template>
