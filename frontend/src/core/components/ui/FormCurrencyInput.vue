<script setup lang="ts">
import { formatCurrency } from "~/core/utils/currency";

const props = withDefaults(
  defineProps<{
    modelValue: number | null;
    id?: string;
    disabled?: boolean;
  }>(),
  { id: undefined, disabled: false },
);

const emit = defineEmits<{ (e: "update:modelValue", value: number | null): void }>();

const autoId = useId();
const inputId = computed(() => props.id ?? autoId);

const focused = ref(false);
const editingText = ref("");

function parseAmount(text: string): number | null {
  const trimmed = text.trim();
  if (trimmed === "") return null;
  // A comma always means "this is the decimal separator" (es-ES), so any dots
  // before it are thousands separators to strip. Without a comma, a lone dot
  // is treated as the decimal point instead (typing "23.5" is as valid as "23,5").
  const normalized = trimmed.includes(",") ? trimmed.replace(/\./g, "").replace(",", ".") : trimmed;
  const value = Number(normalized);
  return Number.isFinite(value) ? value : null;
}

const displayValue = computed(() =>
  props.modelValue === null ? "" : formatCurrency(Math.round(props.modelValue * 100)),
);

function handleFocus(event: FocusEvent) {
  focused.value = true;
  editingText.value = props.modelValue === null ? "" : String(props.modelValue).replace(".", ",");
  (event.target as HTMLInputElement).select();
}

function handleInput(event: Event) {
  editingText.value = (event.target as HTMLInputElement).value;
  emit("update:modelValue", parseAmount(editingText.value));
}

function handleBlur() {
  focused.value = false;
  emit("update:modelValue", parseAmount(editingText.value));
}
</script>

<template>
  <input
    :id="inputId"
    :value="focused ? editingText : displayValue"
    type="text"
    inputmode="decimal"
    autocomplete="off"
    :disabled="disabled"
    class="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-right text-xs text-slate-700 shadow-sm transition-colors focus:border-green-700 focus:outline-none focus:ring-1 focus:ring-green-700 md:text-sm disabled:cursor-not-allowed disabled:opacity-60"
    @focus="handleFocus"
    @input="handleInput"
    @blur="handleBlur"
  />
</template>
