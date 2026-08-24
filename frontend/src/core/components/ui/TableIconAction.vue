<script setup lang="ts">
const props = withDefaults(
  defineProps<{ icon: string; label: string; to?: string; tone?: "neutral" | "success" | "danger" }>(),
  { to: undefined, tone: "neutral" },
);

defineEmits<{ click: [] }>();

const toneClass = computed(
  () =>
    ({
      neutral: "text-slate-500 hover:text-emerald-700",
      success: "text-emerald-600 hover:text-emerald-800",
      danger: "text-red-500 hover:text-red-700",
    })[props.tone],
);
</script>

<template>
  <NuxtLink
    v-if="to"
    :to="to"
    :title="label"
    :aria-label="label"
    class="inline-flex items-center justify-center rounded-md p-1.5 transition-colors hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500"
    :class="toneClass"
  >
    <Icon :name="icon" />
  </NuxtLink>
  <button
    v-else
    type="button"
    :title="label"
    :aria-label="label"
    class="inline-flex items-center justify-center rounded-md p-1.5 transition-colors hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500"
    :class="toneClass"
    @click="$emit('click')"
  >
    <Icon :name="icon" />
  </button>
</template>
