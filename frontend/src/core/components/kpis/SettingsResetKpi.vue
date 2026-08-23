<script setup lang="ts">
const { t } = useI18n();
</script>

<template>
  <p class="text-xs font-medium text-slate-500">{{ t("settings.cards.reset") }}</p>
  <p class="mt-3 text-sm text-red-600">{{ t("settings.cards.resetHint") }}</p>
</template>
