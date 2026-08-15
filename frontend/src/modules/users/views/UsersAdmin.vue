<script setup lang="ts">
import { useAuthStore } from "~/core/stores/auth";
import { listUsers, updateUserRole, type Role, type UserItem } from "~/modules/users/api";

const authStore = useAuthStore();
const users = ref<UserItem[]>([]);
const loading = ref(true);
const errorMessage = ref("");

const roleOptions: { label: string; value: Role }[] = [
  { label: "Admin", value: "admin" },
  { label: "Manager", value: "manager" },
  { label: "User", value: "user" },
];

async function loadUsers() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await listUsers();
    users.value = response.users;
  } catch (error) {
    errorMessage.value = "No se ha podido cargar el listado de miembros.";
  } finally {
    loading.value = false;
  }
}

async function handleRoleChange(user: UserItem, role: Role) {
  const previousRole = user.role;
  user.role = role;
  try {
    await updateUserRole(user.uid, role);
  } catch (error) {
    user.role = previousRole;
    errorMessage.value = `No se ha podido actualizar el rol de ${user.email}.`;
  }
}

onMounted(loadUsers);
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">Gestión de usuarios</h1>
    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <DataTable :value="users" :loading="loading" class="mt-4" data-key="uid">
      <Column header="Usuario">
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
      <Column field="email" header="Email" />
      <Column header="Rol">
        <template #body="{ data }">
          <Dropdown
            v-model="data.role"
            :options="roleOptions"
            option-label="label"
            option-value="value"
            :disabled="!authStore.isAdmin"
            @update:model-value="(role) => handleRoleChange(data, role)"
          />
        </template>
      </Column>
      <Column header="Estado">
        <template #body="{ data }">
          <Tag :severity="data.disabled ? 'danger' : 'success'" :value="data.disabled ? 'Deshabilitado' : 'Activo'" />
        </template>
      </Column>
    </DataTable>
  </div>
</template>
