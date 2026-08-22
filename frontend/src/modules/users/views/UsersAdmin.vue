<script setup lang="ts">
import {
  listUsers,
  updateUserActive,
  updateUserRole,
  type UserItem,
  type UserStatus,
} from "~/modules/users/api";
import { listRoles, type UserRole } from "~/modules/roles/api";
import Card from "~/core/components/ui/Card.vue";
import FormSelect from "~/core/components/ui/FormSelect.vue";
import StatusBadge from "~/core/components/ui/StatusBadge.vue";
import TabNav from "~/core/components/ui/TabNav.vue";
import ToggleSwitch from "~/core/components/ui/ToggleSwitch.vue";
import { tableCellClass, tableHeaderCellClass, tableRowClass } from "~/core/ui/tableClasses";

const { t } = useI18n();

useHead({ title: t("users.title") });

const users = ref<UserItem[]>([]);
const roles = ref<UserRole[]>([]);
const loading = ref(true);
const errorMessage = ref("");
const status = ref<UserStatus>("active");

const statusOptions = computed(() => [
  { label: t("users.filters.active"), value: "active" as UserStatus },
  { label: t("users.filters.new"), value: "new" as UserStatus },
  { label: t("users.filters.inactive"), value: "inactive" as UserStatus },
]);

const roleOptions = computed(() => roles.value.map((role: UserRole) => ({ label: role.name, value: role.id })));

async function loadRoles() {
  try {
    roles.value = await listRoles();
  } catch (error) {
    errorMessage.value = t("users.rolesLoadError");
  }
}

async function loadUsers() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await listUsers(status.value);
    users.value = response.users;
  } catch (error) {
    errorMessage.value = t("users.loadError");
  } finally {
    loading.value = false;
  }
}

async function handleRoleChange(user: UserItem, roleId: string) {
  try {
    await updateUserRole(user.uid, roleId);
    await loadUsers();
  } catch (error) {
    errorMessage.value = t("users.roleUpdateError", { email: user.email });
  }
}

async function handleActiveChange(user: UserItem, active: boolean) {
  try {
    await updateUserActive(user.uid, active);
    await loadUsers();
  } catch (error) {
    errorMessage.value = t("users.activeUpdateError", { email: user.email });
  }
}

watch(status, loadUsers);
onMounted(() => {
  loadRoles();
  loadUsers();
});
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">{{ t("users.title") }}</h1>

    <TabNav v-model="status" :options="statusOptions" class="mt-6" />

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <Card class="mt-4 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="bg-slate-50">
              <th :class="tableHeaderCellClass">{{ t("users.columns.user") }}</th>
              <th :class="tableHeaderCellClass">{{ t("users.columns.email") }}</th>
              <th :class="tableHeaderCellClass">{{ t("users.columns.role") }}</th>
              <th :class="tableHeaderCellClass">{{ t("users.columns.active") }}</th>
              <th :class="[tableHeaderCellClass, 'text-right']">{{ t("users.columns.actions") }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="5" class="px-4 py-6 text-center text-slate-500">{{ t("users.loading") }}</td>
            </tr>
            <tr v-else-if="users.length === 0">
              <td colspan="5" class="px-4 py-6 text-center text-slate-500">{{ t("users.empty") }}</td>
            </tr>
            <tr v-for="user in users" :key="user.uid" :class="tableRowClass">
              <td :class="tableCellClass">
                <div class="flex items-center gap-2">
                  <img
                    v-if="user.photo_url"
                    :src="user.photo_url"
                    :alt="user.display_name ?? user.email ?? ''"
                    class="h-8 w-8 rounded-full"
                  />
                  <span>{{ user.display_name ?? "—" }}</span>
                </div>
              </td>
              <td :class="[tableCellClass, 'text-slate-600']">{{ user.email }}</td>
              <td :class="tableCellClass">
                <div class="flex items-center">
                  <FormSelect
                    :model-value="user.role_id ?? ''"
                    @update:model-value="(role) => handleRoleChange(user, role)"
                  >
                    <option value="" disabled>{{ t("users.noRole") }}</option>
                    <option v-for="role in roleOptions" :key="role.value" :value="role.value">
                      {{ role.label }}
                    </option>
                  </FormSelect>
                </div>
              </td>
              <td :class="tableCellClass">
                <div class="flex items-center">
                  <StatusBadge v-if="status === 'inactive'" :label="t('users.status.inactive')" />
                  <ToggleSwitch
                    v-else
                    :model-value="!user.disabled"
                    @update:model-value="(active) => handleActiveChange(user, active)"
                  />
                </div>
              </td>
              <td :class="[tableCellClass, 'text-right']">
                <div class="flex items-center justify-end">
                  <button
                    v-if="status === 'inactive'"
                    type="button"
                    class="rounded text-sm font-medium text-indigo-600 hover:text-indigo-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                    @click="handleActiveChange(user, true)"
                  >
                    {{ t("users.actions.reactivate") }}
                  </button>
                  <span v-else class="text-slate-400">—</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  </div>
</template>
