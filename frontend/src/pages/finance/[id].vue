<script setup lang="ts">
import MovementForm from "~/modules/finance/components/MovementForm.vue";

const route = useRoute();
</script>

<template>
  <MovementForm :movement-id="route.params.id as string" />
</template>
