<script setup lang="ts">
import { usePermissionsStore } from "~/core/stores/permissions";
import UsersAdmin from "~/modules/users/views/UsersAdmin.vue";

const permissionsStore = usePermissionsStore();

if (!permissionsStore.has("SYSTEM_ADMIN")) {
  await navigateTo("/home");
}
</script>

<template>
  <UsersAdmin />
</template>
