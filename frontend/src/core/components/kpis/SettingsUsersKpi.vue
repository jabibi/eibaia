<script setup lang="ts">
import type { UsersSummary } from "~/modules/users/api";

defineProps<{ loading: boolean; summary?: UsersSummary | null }>();
const { t } = useI18n();
</script>

<template>
  <p class="text-xs font-medium text-slate-500">{{ t("settings.cards.users") }}</p>
  <div class="mt-3 flex items-center gap-6">
    <div>
      <p class="text-2xl font-bold text-slate-900">{{ loading ? "…" : (summary?.active ?? 0) }}</p>
      <p class="text-xs text-slate-500">{{ t("users.filters.active") }}</p>
    </div>
    <div>
      <p class="text-2xl font-bold text-emerald-600">{{ loading ? "…" : (summary?.new ?? 0) }}</p>
      <p class="text-xs text-slate-500">{{ t("users.filters.new") }}</p>
    </div>
    <div>
      <p class="text-2xl font-bold text-slate-500">{{ loading ? "…" : (summary?.inactive ?? 0) }}</p>
      <p class="text-xs text-slate-500">{{ t("users.filters.inactive") }}</p>
    </div>
  </div>
</template>
