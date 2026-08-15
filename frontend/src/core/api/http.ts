import { useAuthStore } from "~/core/stores/auth";

export async function apiFetch<T>(path: string, options: Parameters<typeof $fetch>[1] = {}) {
  const config = useRuntimeConfig();
  const authStore = useAuthStore();
  const token = await authStore.getIdToken();

  return $fetch<T>(path, {
    baseURL: config.public.apiBase,
    ...options,
    headers: {
      ...(options.headers as Record<string, string> | undefined),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
}
