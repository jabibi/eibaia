<script setup lang="ts">
import { useCashboxStore } from "~/core/stores/cashbox";

const cashboxStore = useCashboxStore();

const label = computed(() => cashboxStore.cashbox?.ribbon_label ?? null);
</script>

<template>
  <div
    v-if="label"
    class="pointer-events-none fixed bottom-0 right-0 z-50 h-20 w-20 select-none overflow-hidden"
    aria-hidden="true"
  >
    <div
      class="absolute -right-6 bottom-3 w-24 -rotate-45 bg-amber-500/85 py-0.5 text-center text-[9px] font-bold uppercase tracking-widest text-white shadow-sm backdrop-blur-[2px]"
    >
      {{ label }}
    </div>
  </div>
</template>
