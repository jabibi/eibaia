<script setup lang="ts">
// Declarados aunque no se usen (no tiene datos propios ni acciones que deshabilitar en modo
// edición) — así ni `loading` ni `editing`, que /home pasa por igual a todos los KPI, hacen
// que Vue avise de un atributo no declarado en este componente multi-root.
defineProps<{ loading?: boolean; editing?: boolean }>();
const { t } = useI18n();
</script>

<template>
  <p class="text-xs font-medium text-slate-500">{{ t("settings.cards.reset") }}</p>
  <p class="mt-3 text-sm text-red-600">{{ t("settings.cards.resetHint") }}</p>
</template>
