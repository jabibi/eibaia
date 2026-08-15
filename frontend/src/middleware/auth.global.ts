import { useAuthStore } from "~/core/stores/auth";

export default defineNuxtRouteMiddleware(async (to) => {
  const authStore = useAuthStore();

  if (!authStore.ready) {
    await authStore.init();
  }

  const isLoginPage = to.path === "/";

  if (!authStore.isAuthenticated && !isLoginPage) {
    return navigateTo("/");
  }

  if (authStore.isAuthenticated && isLoginPage) {
    return navigateTo("/inicio");
  }
});
