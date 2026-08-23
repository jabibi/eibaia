<script setup lang="ts">
import { useDashboardPreferencesStore } from "~/core/stores/dashboardPreferences";

const props = withDefaults(
  defineProps<{
    to: string;
    variant?: "default" | "warning" | "danger" | "featured";
    kpiId?: string;
    showStar?: boolean;
  }>(),
  { variant: "default", kpiId: undefined, showStar: true },
);

const dashboardPreferences = useDashboardPreferencesStore();
const { t } = useI18n();

const isPinned = computed(() => (props.kpiId ? dashboardPreferences.isPinned(props.kpiId) : false));

function toggleStar() {
  if (props.kpiId) dashboardPreferences.toggle(props.kpiId);
}
</script>

<template>
  <div
    class="group relative rounded-lg border p-6 shadow-sm transition hover:shadow-md"
    :class="{
      'border-slate-200 bg-white hover:border-emerald-300': variant === 'default',
      'border-slate-200 bg-white hover:border-amber-300': variant === 'warning',
      'border-red-200 bg-red-50/30 hover:border-red-300': variant === 'danger',
      'border-emerald-200 bg-emerald-50/50 hover:bg-emerald-50 hover:shadow-md': variant === 'featured',
    }"
  >
    <NuxtLink
      :to="to"
      class="absolute inset-0 rounded-lg focus-visible:outline-none focus-visible:ring-2"
      :class="variant === 'danger' ? 'focus-visible:ring-red-500' : 'focus-visible:ring-indigo-500'"
    />
    <button
      v-if="kpiId && showStar"
      type="button"
      class="absolute right-3 top-3 z-10 rounded-full p-1 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
      :aria-label="isPinned ? t('home.unpinKpi') : t('home.pinKpi')"
      @click.stop.prevent="toggleStar"
    >
      <Icon name="lucide:star" :class="isPinned ? 'text-amber-400' : 'text-slate-300 hover:text-slate-400'" />
    </button>
    <div class="pointer-events-none relative">
      <slot />
    </div>
  </div>
</template>
