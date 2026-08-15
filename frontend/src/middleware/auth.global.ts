import { useAuthStore } from "~/core/stores/auth";

export default defineNuxtRouteMiddleware(async (to) => {
  const authStore = useAuthStore();

  if (!authStore.ready) {
    await authStore.init();
  }

  const isLoginPage = to.path === "/";
  const isPendingPage = to.path === "/pending";

  if (!authStore.isAuthenticated) {
    return isLoginPage ? undefined : navigateTo("/");
  }

  if (!authStore.isApproved) {
    return isPendingPage ? undefined : navigateTo("/pending");
  }

  if (isLoginPage || isPendingPage) {
    return navigateTo("/home");
  }
});
