<script setup lang="ts">
import { useAuthStore } from "~/core/stores/auth";
import UsersAdmin from "~/modules/users/views/UsersAdmin.vue";

const authStore = useAuthStore();

if (!authStore.isAdmin) {
  await navigateTo("/home");
}
</script>

<template>
  <UsersAdmin />
</template>
