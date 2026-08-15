<script setup lang="ts">
import {
  listUsers,
  updateUserActive,
  updateUserRole,
  type Role,
  type UserItem,
  type UserStatus,
} from "~/modules/users/api";

const { t } = useI18n();

const users = ref<UserItem[]>([]);
const loading = ref(true);
const errorMessage = ref("");
const status = ref<UserStatus>("active");

const statusOptions = computed(() => [
  { label: t("users.filters.active"), value: "active" as UserStatus },
  { label: t("users.filters.new"), value: "new" as UserStatus },
  { label: t("users.filters.inactive"), value: "inactive" as UserStatus },
]);

const roleOptions: { label: string; value: Role }[] = [
  { label: "Admin", value: "admin" },
  { label: "Manager", value: "manager" },
  { label: "User", value: "user" },
];

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

async function handleRoleChange(user: UserItem, role: Role) {
  try {
    await updateUserRole(user.uid, role);
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
onMounted(loadUsers);
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">{{ t("users.title") }}</h1>

    <SelectButton
      v-model="status"
      :options="statusOptions"
      option-label="label"
      option-value="value"
      class="mt-4"
    />

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <DataTable :value="users" :loading="loading" class="mt-4" data-key="uid">
      <Column :header="t('users.columns.user')">
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <img
              v-if="data.photo_url"
              :src="data.photo_url"
              :alt="data.display_name"
              class="h-8 w-8 rounded-full"
            />
            <span>{{ data.display_name ?? "—" }}</span>
          </div>
        </template>
      </Column>
      <Column field="email" :header="t('users.columns.email')" />
      <Column :header="t('users.columns.role')">
        <template #body="{ data }">
          <Dropdown
            :model-value="data.role"
            :options="roleOptions"
            option-label="label"
            option-value="value"
            :placeholder="t('users.noRole')"
            @update:model-value="(role) => handleRoleChange(data, role)"
          />
        </template>
      </Column>
      <Column :header="t('users.columns.active')">
        <template #body="{ data }">
          <InputSwitch
            :model-value="!data.disabled"
            @update:model-value="(active) => handleActiveChange(data, active)"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>
