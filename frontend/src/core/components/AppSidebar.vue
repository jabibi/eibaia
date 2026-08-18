<script setup lang="ts">
import GithubLink from "~/core/components/GithubLink.vue";
import { useSidebar } from "~/core/composables/useSidebar";
import { useAuthStore } from "~/core/stores/auth";
import { usePermissionsStore } from "~/core/stores/permissions";

const authStore = useAuthStore();
const permissionsStore = usePermissionsStore();
const { t } = useI18n();
const sidebar = useSidebar();
const { collapsed, mobileOpen } = sidebar;

sidebar.restoreFromStorage();

/** On mobile this just closes the drawer (unchanged mobile behavior). On
 * desktop this single button both expands a collapsed sidebar and collapses
 * an expanded one — it's the only way to expand it. */
function handleLogoClick() {
  if (mobileOpen.value) {
    sidebar.closeMobile();
    return;
  }
  if (collapsed.value) {
    sidebar.expand();
  } else {
    sidebar.collapse();
  }
}

/** Clicking empty space in the desktop sidebar (i.e. not a link or button)
 * toggles it — collapses when expanded, expands when collapsed — matching
 * the w-resize/e-resize cursor shown over that same empty space. Clicking a
 * menu item itself just navigates. */
function handleAsideBackgroundClick(event: MouseEvent) {
  if (mobileOpen.value) return;
  const target = event.target as HTMLElement;
  if (target.closest("a, button")) return;
  if (collapsed.value) {
    sidebar.expand();
  } else {
    sidebar.collapse();
  }
}

const menuItems = computed(() => [
  { label: t("sidebar.home"), icon: "pi pi-home", to: "/home", permissions: [] as string[] },
  { label: t("sidebar.finance"), icon: "pi pi-wallet", to: "/finance", permissions: ["CASHBOX_BASIC"] },
  { label: t("sidebar.settings"), icon: "pi pi-cog", to: "/settings", permissions: ["SYSTEM_ADMIN"] },
]);

function isVisible(item: { permissions: string[] }): boolean {
  return item.permissions.length === 0 || item.permissions.some((code) => permissionsStore.has(code));
}

const visibleItems = computed(() => menuItems.value.filter(isVisible));

async function handleLogout() {
  await authStore.logout();
  await navigateTo("/");
}
</script>

<template>
  <button
    v-show="!mobileOpen"
    type="button"
    :aria-label="t('sidebar.expandMenu')"
    class="fixed left-3 top-3 z-30 flex h-10 w-10 items-center justify-center rounded-md bg-white text-slate-600 shadow ring-1 ring-slate-200 md:hidden"
    @click="sidebar.openMobile()"
  >
    <i class="pi pi-bars text-lg" />
  </button>

  <div
    v-if="mobileOpen"
    class="fixed inset-0 z-30 bg-black/40 md:hidden"
    @click="sidebar.closeMobile()"
  />

  <aside
    class="fixed left-0 top-0 z-40 flex h-svh w-[85%] max-w-xs -translate-x-full flex-col bg-white transition-transform duration-200 md:relative md:z-auto md:translate-x-0 md:transition-all"
    :class="[
      mobileOpen ? 'translate-x-0' : '-translate-x-full',
      collapsed ? 'md:w-[52px]' : 'md:w-64',
      !mobileOpen && collapsed ? 'md:cursor-e-resize' : '',
      !mobileOpen && !collapsed ? 'md:cursor-w-resize' : '',
    ]"
    @click="handleAsideBackgroundClick"
  >
    <div class="flex items-center gap-1 px-3 py-4" :class="collapsed && !mobileOpen ? 'md:justify-center md:px-1.5' : ''">
      <button
        type="button"
        v-tooltip.right="!mobileOpen ? (collapsed ? t('sidebar.expandMenu') : t('sidebar.collapseMenu')) : undefined"
        :aria-label="collapsed ? t('sidebar.expandMenu') : t('sidebar.collapseMenu')"
        class="flex shrink-0 cursor-pointer items-center gap-2 rounded-md hover:bg-slate-100"
        :class="collapsed && !mobileOpen ? 'md:h-10 md:w-10 md:justify-center md:cursor-e-resize' : 'flex-1 py-1 md:cursor-w-resize'"
        @click="handleLogoClick"
      >
        <span class="flex h-8 w-8 shrink-0 items-center justify-center">
          <img :src="'/img/favicon.svg'" alt="ElosuE!" class="h-9 w-9" />
        </span>
        <span v-if="!collapsed || mobileOpen" class="truncate text-lg font-semibold">
          <span style="color: #15803d">Elosu</span><span style="color: #dc2626">E!</span>
        </span>
        <i v-if="!collapsed" class="pi pi-chevron-left ml-auto hidden shrink-0 text-xs text-slate-600 md:block" />
        <i class="pi pi-times ml-auto shrink-0 text-lg text-slate-600 md:hidden" />
      </button>
    </div>

    <nav class="flex-1 space-y-1 overflow-y-auto px-2" :class="collapsed && !mobileOpen ? 'md:px-1.5' : ''">
      <NuxtLink
        v-for="item in visibleItems"
        :key="item.to"
        :to="item.to"
        v-tooltip.right="collapsed && !mobileOpen ? item.label : undefined"
        class="flex cursor-pointer items-center gap-3 rounded-md text-sm text-slate-600 hover:bg-slate-100"
        active-class="bg-slate-100 text-slate-900 font-medium"
        :class="collapsed && !mobileOpen ? 'md:h-10 md:w-10 md:justify-center md:gap-0 md:px-0' : 'px-3 py-2'"
      >
        <i :class="item.icon" class="text-lg shrink-0" />
        <span v-if="!collapsed || mobileOpen" class="truncate">{{ item.label }}</span>
      </NuxtLink>
    </nav>

    <div class="p-2" :class="collapsed && !mobileOpen ? 'md:px-1.5' : ''">
      <button
        type="button"
        v-tooltip.right="collapsed && !mobileOpen ? t('sidebar.logout') : undefined"
        class="flex cursor-pointer items-center gap-3 rounded-md text-sm text-slate-600 hover:bg-slate-100"
        :class="collapsed && !mobileOpen ? 'md:h-10 md:w-10 md:justify-center md:gap-0' : 'w-full px-3 py-2'"
        @click="handleLogout"
      >
        <i class="pi pi-sign-out text-lg shrink-0" />
        <span v-if="!collapsed || mobileOpen">{{ t("sidebar.logout") }}</span>
      </button>

      <div class="mt-2 flex justify-center">
        <GithubLink size="h-4 w-4" class="cursor-pointer" />
      </div>
    </div>
  </aside>
</template>
