<script setup lang="ts">
import GithubLink from "~/core/components/GithubLink.vue";
import { useAuthStore } from "~/core/stores/auth";

const STORAGE_KEY = "elosue:sidebar-collapsed";

const authStore = useAuthStore();
const collapsed = ref(false);

if (import.meta.client) {
  collapsed.value = localStorage.getItem(STORAGE_KEY) === "1";
}

function toggleCollapsed() {
  collapsed.value = !collapsed.value;
  if (import.meta.client) {
    localStorage.setItem(STORAGE_KEY, collapsed.value ? "1" : "0");
  }
}

const menuItems = [
  { label: "Inicio", icon: "pi pi-home", to: "/inicio", roles: ["admin", "manager", "user"] },
  { label: "Caja Fuerte", icon: "pi pi-wallet", to: "/finanzas", roles: ["admin", "manager", "user"] },
  { label: "Calendario", icon: "pi pi-calendar", to: "/calendario", roles: ["admin", "manager", "user"] },
  { label: "Horarios", icon: "pi pi-clock", to: "/horarios", roles: ["admin", "manager", "user"] },
  { label: "Usuarios", icon: "pi pi-users", to: "/usuarios", roles: ["admin", "manager"] },
];

const visibleItems = computed(() =>
  menuItems.filter((item) => item.roles.includes(authStore.role)),
);

async function handleLogout() {
  await authStore.logout();
  await navigateTo("/");
}
</script>

<template>
  <aside
    class="flex h-screen flex-col border-r border-slate-200 bg-white transition-all duration-200"
    :class="collapsed ? 'w-16' : 'w-64'"
  >
    <div class="flex items-center gap-2 px-3 py-4" :class="collapsed ? 'justify-center' : ''">
      <button
        type="button"
        v-tooltip.right="collapsed ? 'Expandir menú' : 'Colapsar menú'"
        class="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-md hover:bg-slate-100"
        @click="toggleCollapsed"
      >
        <img :src="'/img/favicon.svg'" alt="ElosuE!" class="h-7 w-7" />
        <i
          :class="collapsed ? 'pi pi-angle-right' : 'pi pi-angle-left'"
          class="absolute -bottom-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-white text-[10px] text-slate-600 shadow ring-1 ring-slate-200"
        />
      </button>
      <span v-if="!collapsed" class="truncate text-lg font-semibold">
        <span style="color: #15803d">Elosu</span><span style="color: #dc2626">E!</span>
      </span>
    </div>

    <nav class="flex-1 space-y-1 px-2">
      <NuxtLink
        v-for="item in visibleItems"
        :key="item.to"
        :to="item.to"
        v-tooltip.right="collapsed ? item.label : undefined"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
        active-class="bg-slate-100 text-slate-900 font-medium"
        :class="collapsed ? 'justify-center' : ''"
      >
        <i :class="item.icon" class="text-lg shrink-0" />
        <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
      </NuxtLink>
    </nav>

    <div class="border-t border-slate-200 p-2">
      <button
        type="button"
        v-tooltip.right="collapsed ? 'Cerrar sesión' : undefined"
        class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
        :class="collapsed ? 'justify-center' : ''"
        @click="handleLogout"
      >
        <i class="pi pi-sign-out text-lg shrink-0" />
        <span v-if="!collapsed">Cerrar sesión</span>
      </button>

      <div class="mt-2 flex justify-center">
        <GithubLink size="h-4 w-4" />
      </div>
    </div>
  </aside>
</template>
