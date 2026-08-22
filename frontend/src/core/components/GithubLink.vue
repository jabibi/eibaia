<script setup lang="ts">
withDefaults(defineProps<{ size?: string }>(), { size: "text-lg" });
</script>

<template>
  <a
    href="https://github.com/jabibi/elosue"
    target="_blank"
    rel="noreferrer"
    aria-label="GitHub"
    class="inline-flex items-center gap-1.5 rounded text-slate-500 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
  >
    <Icon name="simple-icons:github" :class="size" />
    <span v-if="$slots.default" class="translate-y-px text-xs"><slot /></span>
  </a>
</template>
