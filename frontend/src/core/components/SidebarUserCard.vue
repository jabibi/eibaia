<script setup lang="ts">
import StatusBadge from "~/core/components/ui/StatusBadge.vue";
import { useAuthStore } from "~/core/stores/auth";

defineProps<{ iconOnly: boolean }>();

const authStore = useAuthStore();
const { t } = useI18n();

/** Role slugs are the fixed set seeded by scripts/seed_rbac.py. Custom roles an
 * admin creates later via the roles UI fall back to showing their raw id, since
 * /roles (with the human-readable name) requires SYSTEM_ADMIN to call. */
const ROLE_LABEL_KEYS: Record<string, string> = {
  admin: "sidebar.roles.admin",
  manager: "sidebar.roles.manager",
  employee: "sidebar.roles.employee",
  user: "sidebar.roles.user",
};
const roleLabel = computed(() => {
  const roleId = authStore.roleId;
  if (!roleId) return null;
  const key = ROLE_LABEL_KEYS[roleId];
  return key ? t(key) : roleId;
});
</script>

<template>
  <div class="mb-1">
    <div v-if="!iconOnly && roleLabel" class="mb-1">
      <StatusBadge :label="roleLabel" />
    </div>

    <!-- No justify-center here: the avatar always starts at the same left edge
    (matching SidebarNavItem's icon column) so it doesn't shift position when
    the name/email column below is hidden in icon-only mode. -->
    <div class="flex items-center gap-2 py-1">
      <img
        v-if="authStore.user?.photoURL"
        :title="iconOnly ? authStore.user?.email ?? undefined : undefined"
        :src="authStore.user.photoURL"
        :alt="authStore.user.displayName ?? authStore.user.email ?? ''"
        class="h-9 w-9 shrink-0 rounded-full object-cover"
      />
      <Icon
        v-else
        name="lucide:user"
        :title="iconOnly ? authStore.user?.email ?? undefined : undefined"
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-500"
      />

      <div v-if="!iconOnly" class="min-w-0 flex-1">
        <p class="truncate text-sm font-medium text-slate-800">
          {{ authStore.user?.displayName ?? authStore.user?.email }}
        </p>
        <p class="truncate text-xs text-slate-500">{{ authStore.user?.email }}</p>
      </div>
    </div>
  </div>
</template>
