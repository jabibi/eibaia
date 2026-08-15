<script setup lang="ts">
const { t } = useI18n();
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">{{ t("calendar.title") }}</h1>
    <p class="mt-2 text-slate-500">{{ t("calendar.comingSoon") }}</p>
  </div>
</template>
