<script setup lang="ts">
import GithubLink from "~/core/components/GithubLink.vue";
import { useSidebar } from "~/core/composables/useSidebar";
import { useAuthStore } from "~/core/stores/auth";

const authStore = useAuthStore();
const { t } = useI18n();
const route = useRoute();
const sidebar = useSidebar();
const { collapsed, mobileOpen } = sidebar;
const expandedGroups = ref<Record<string, boolean>>({});

sidebar.restoreFromStorage();

function toggleGroup(key: string) {
  expandedGroups.value[key] = !expandedGroups.value[key];
}

function isGroupExpanded(item: { to: string; children?: { to: string }[] }): boolean {
  const isActive = route.path === item.to || Boolean(item.children?.some((child) => route.path.startsWith(child.to)));
  return isActive || Boolean(expandedGroups.value[item.to]);
}

/** Clicking anywhere on the collapsed rail expands it (desktop only — on
 * mobile the rail is off-screen while closed, so this can only fire when the
 * mobile drawer is already open, where it must not touch desktop state). */
function handleAsideClick() {
  if (mobileOpen.value) return;
  sidebar.expand();
}

const menuItems = computed(() => [
  { label: t("sidebar.home"), icon: "pi pi-home", to: "/home", roles: ["admin", "manager", "user"] },
  {
    label: t("sidebar.finance"),
    icon: "pi pi-wallet",
    to: "/finance",
    roles: ["admin", "manager", "user"],
    children: [
      { label: t("sidebar.financeTransactions"), to: "/finance/transactions", roles: ["admin", "manager", "user"] },
      { label: t("sidebar.financeReview"), to: "/finance/review", roles: ["admin", "manager"] },
    ],
  },
  { label: t("sidebar.calendar"), icon: "pi pi-calendar", to: "/calendar", roles: ["admin", "manager", "user"] },
  { label: t("sidebar.schedule"), icon: "pi pi-clock", to: "/schedule", roles: ["admin", "manager", "user"] },
  {
    label: t("sidebar.settings"),
    icon: "pi pi-cog",
    to: "/settings",
    roles: ["admin"],
    children: [
      { label: t("sidebar.users"), to: "/settings/users", roles: ["admin"] },
      { label: t("sidebar.reset"), to: "/settings/reset", roles: ["admin"] },
    ],
  },
]);

const visibleItems = computed(() =>
  menuItems.value
    .filter((item) => item.roles.includes(authStore.role))
    .map((item) => ({
      ...item,
      children: item.children?.filter((child) => child.roles.includes(authStore.role)),
    })),
);

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
    class="fixed left-0 top-0 z-40 flex h-svh w-[85%] max-w-xs -translate-x-full flex-col border-r border-slate-200 bg-white transition-transform duration-200 md:relative md:z-auto md:w-16 md:translate-x-0 md:transition-all"
    :class="[mobileOpen ? 'translate-x-0' : '-translate-x-full', collapsed ? 'md:w-16' : 'md:w-64']"
    @click="handleAsideClick"
  >
    <button
      type="button"
      :aria-label="collapsed ? t('sidebar.expandMenu') : t('sidebar.collapseMenu')"
      class="absolute -right-3 top-1/2 hidden h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-500 shadow hover:bg-slate-50 md:flex"
      @click.stop="sidebar.toggleCollapsed()"
    >
      <i :class="collapsed ? 'pi pi-angle-right' : 'pi pi-angle-left'" class="text-[10px]" />
    </button>

    <div class="flex items-center gap-1 px-3 py-4">
      <button
        type="button"
        :aria-label="t('sidebar.collapseMenu')"
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-slate-600 hover:bg-slate-100 md:hidden"
        @click="sidebar.closeMobile()"
      >
        <i class="pi pi-times text-lg" />
      </button>

      <button
        type="button"
        v-tooltip.right="collapsed ? t('sidebar.expandMenu') : t('sidebar.collapseMenu')"
        class="flex flex-1 items-center gap-2 rounded-md py-1 hover:bg-slate-100"
        :class="collapsed && !mobileOpen ? 'md:justify-center' : ''"
        @click.stop="sidebar.handleHeaderToggle()"
      >
        <span class="flex h-9 w-9 shrink-0 items-center justify-center">
          <img :src="'/img/favicon.svg'" alt="ElosuE!" class="h-9 w-9" />
        </span>
        <span v-if="!collapsed || mobileOpen" class="truncate text-lg font-semibold">
          <span style="color: #15803d">Elosu</span><span style="color: #dc2626">E!</span>
        </span>
      </button>
    </div>

    <nav class="flex-1 space-y-1 overflow-y-auto px-2">
      <template v-for="item in visibleItems" :key="item.to">
        <div class="flex items-center">
          <NuxtLink
            :to="item.to"
            v-tooltip.right="collapsed && !mobileOpen ? item.label : undefined"
            class="flex flex-1 items-center gap-3 rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
            active-class="bg-slate-100 text-slate-900 font-medium"
            :class="collapsed && !mobileOpen ? 'md:justify-center' : ''"
          >
            <i :class="item.icon" class="text-lg shrink-0" />
            <span v-if="!collapsed || mobileOpen" class="truncate">{{ item.label }}</span>
          </NuxtLink>
          <button
            v-if="(!collapsed || mobileOpen) && item.children?.length"
            type="button"
            class="mr-1 shrink-0 rounded-md p-2 text-slate-400 hover:bg-slate-100"
            @click="toggleGroup(item.to)"
          >
            <i :class="isGroupExpanded(item) ? 'pi pi-chevron-down' : 'pi pi-chevron-right'" class="text-xs" />
          </button>
        </div>

        <div v-if="(!collapsed || mobileOpen) && item.children?.length && isGroupExpanded(item)" class="ml-6 space-y-1">
          <NuxtLink
            v-for="child in item.children"
            :key="child.to"
            :to="child.to"
            class="flex items-center gap-2 rounded-md px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100"
            active-class="bg-slate-100 text-slate-900 font-medium"
          >
            <span class="truncate">{{ child.label }}</span>
          </NuxtLink>
        </div>
      </template>
    </nav>

    <div class="border-t border-slate-200 p-2">
      <button
        type="button"
        v-tooltip.right="collapsed && !mobileOpen ? t('sidebar.logout') : undefined"
        class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
        :class="collapsed && !mobileOpen ? 'md:justify-center' : ''"
        @click="handleLogout"
      >
        <i class="pi pi-sign-out text-lg shrink-0" />
        <span v-if="!collapsed || mobileOpen">{{ t("sidebar.logout") }}</span>
      </button>

      <div class="mt-2 flex justify-center">
        <GithubLink size="h-4 w-4" />
      </div>
    </div>
  </aside>
</template>
