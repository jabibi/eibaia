<script setup lang="ts">
withDefaults(defineProps<{ size?: string }>(), { size: "text-lg" });
</script>

<template>
  <a
    href="https://github.com/jabibi/elosue"
    target="_blank"
    rel="noreferrer"
    aria-label="GitHub"
    class="inline-flex items-center gap-1.5 text-slate-400 hover:text-slate-700"
  >
    <Icon name="lucide:github" :class="size" />
    <span v-if="$slots.default" class="text-[10px]"><slot /></span>
  </a>
</template>
