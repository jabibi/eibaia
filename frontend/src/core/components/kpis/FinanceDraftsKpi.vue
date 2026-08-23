<script setup lang="ts">
import type { FinanceSummary } from "~/modules/finance/api";

defineProps<{ loading: boolean; summary?: FinanceSummary | null }>();
const { t } = useI18n();
</script>

<template>
  <p class="text-xs font-medium text-slate-500">{{ t("finance.kpi.drafts") }}</p>
  <p
    class="mt-2 text-2xl font-bold"
    :class="(summary?.pending_drafts_count ?? 0) > 0 ? 'text-amber-600' : 'text-slate-900'"
  >
    {{ loading ? "…" : (summary?.pending_drafts_count ?? 0) }}
  </p>
  <p class="mt-1 text-xs text-slate-500">{{ t("finance.kpi.draftsHint") }}</p>
</template>
