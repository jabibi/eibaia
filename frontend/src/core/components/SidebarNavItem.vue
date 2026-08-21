<script setup lang="ts">
withDefaults(
  defineProps<{
    icon: string;
    label: string;
    to?: string;
    iconOnly?: boolean;
    tooltip?: string;
    variant?: "default" | "danger";
  }>(),
  { to: undefined, iconOnly: false, tooltip: undefined, variant: "default" },
);

defineEmits<{ click: [] }>();
</script>

<template>
  <NuxtLink
    v-if="to"
    :to="to"
    v-tooltip.right="tooltip"
    class="flex h-10 cursor-pointer items-center gap-3 rounded-md text-sm text-slate-600"
    :class="[
      variant === 'danger' ? 'hover:bg-red-50 hover:text-red-600' : 'hover:bg-slate-100',
      iconOnly ? 'md:w-10 md:justify-center md:gap-0 md:px-0' : 'w-full px-2',
    ]"
    active-class="bg-slate-100 text-slate-900 font-medium"
    @click="$emit('click')"
  >
    <i :class="icon" class="text-lg shrink-0" />
    <span v-if="!iconOnly" class="truncate">{{ label }}</span>
  </NuxtLink>
  <button
    v-else
    type="button"
    v-tooltip.right="tooltip"
    class="flex h-10 cursor-pointer items-center gap-3 rounded-md text-sm text-slate-600"
    :class="[
      variant === 'danger' ? 'hover:bg-red-50 hover:text-red-600' : 'hover:bg-slate-100',
      iconOnly ? 'md:w-10 md:justify-center md:gap-0 md:px-0' : 'w-full px-2',
    ]"
    @click="$emit('click')"
  >
    <i :class="icon" class="text-lg shrink-0" />
    <span v-if="!iconOnly" class="truncate">{{ label }}</span>
  </button>
</template>
