<script setup lang="ts">
withDefaults(
  defineProps<{
    icon: string;
    label: string;
    to?: string;
    iconOnly?: boolean;
    tooltip?: string;
    variant?: "default" | "danger";
  }>(),
  { to: undefined, iconOnly: false, tooltip: undefined, variant: "default" },
);

defineEmits<{ click: [] }>();
</script>

<template>
  <NuxtLink
    v-if="to"
    :to="to"
    :aria-label="iconOnly ? label : undefined"
    :title="tooltip"
    class="flex h-10 cursor-pointer items-center rounded-md text-sm text-slate-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-700"
    :class="[
      variant === 'danger' ? 'hover:bg-red-50 hover:text-red-600' : 'hover:bg-slate-100',
      iconOnly ? 'md:w-10' : 'w-full',
    ]"
    active-class="bg-slate-100 text-slate-900 font-medium"
    @click="$emit('click')"
  >
    <!-- Columna de icono a tamaño fijo (40x40) siempre, en los dos modos —
    así el icono no se desplaza al desplegar el panel: lo único que cambia es
    que aparece la etiqueta a continuación, la columna del icono no se mueve
    ni cambia de tamaño (mismo criterio que el avatar de SidebarUserCard). -->
    <span class="flex h-10 w-10 shrink-0 items-center justify-center">
      <Icon :name="icon" class="text-lg shrink-0" />
    </span>
    <span v-if="!iconOnly" class="truncate">{{ label }}</span>
  </NuxtLink>
  <button
    v-else
    type="button"
    :aria-label="iconOnly ? label : undefined"
    :title="tooltip"
    class="flex h-10 cursor-pointer items-center rounded-md text-sm text-slate-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-700"
    :class="[
      variant === 'danger' ? 'hover:bg-red-50 hover:text-red-600' : 'hover:bg-slate-100',
      iconOnly ? 'md:w-10' : 'w-full',
    ]"
    @click="$emit('click')"
  >
    <span class="flex h-10 w-10 shrink-0 items-center justify-center">
      <Icon :name="icon" class="text-lg shrink-0" />
    </span>
    <span v-if="!iconOnly" class="truncate">{{ label }}</span>
  </button>
</template>
