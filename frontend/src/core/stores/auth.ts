import { defineStore } from "pinia";
import {
  type User,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
} from "firebase/auth";
import { usePermissionsStore } from "~/core/stores/permissions";

interface AuthState {
  user: User | null;
  roleId: string | null;
  ready: boolean;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    user: null,
    roleId: null,
    ready: false,
  }),

  getters: {
    isAuthenticated: (state) => state.user !== null,
    isApproved: (state) => state.roleId !== null,
  },

  actions: {
    async init() {
      const { $firebaseAuth } = useNuxtApp();

      return new Promise<void>((resolve) => {
        onAuthStateChanged($firebaseAuth, async (user) => {
          this.user = user;
          this.roleId = user ? await syncRoleId(user) : null;
          if (user) {
            await usePermissionsStore().load();
          } else {
            usePermissionsStore().clear();
          }
          this.ready = true;
          resolve();
        });
      });
    },

    async loginWithGoogle() {
      const { $firebaseAuth, $googleProvider } = useNuxtApp();
      const { user } = await signInWithPopup($firebaseAuth, $googleProvider);
      this.user = user;
      this.roleId = await syncRoleId(user);
      await usePermissionsStore().load();
    },

    async logout() {
      const { $firebaseAuth } = useNuxtApp();
      await signOut($firebaseAuth);
      usePermissionsStore().clear();
      this.user = null;
      this.roleId = null;
    },

    async getIdToken(forceRefresh = false) {
      return this.user?.getIdToken(forceRefresh) ?? null;
    },
  },
});

async function resolveRoleId(user: User): Promise<string | null> {
  const { claims } = await user.getIdTokenResult();
  return (claims.role_id as string) ?? null;
}

/**
 * Resolves the role_id from the token and cross-checks it against the backend, which may
 * promote the first-ever registered user to admin (see ensure_first_admin). If the backend
 * returns a different role_id, forces an ID token refresh. A `null` role_id means no role has
 * been assigned yet (no access).
 */
async function syncRoleId(user: User): Promise<string | null> {
  const tokenRoleId = await resolveRoleId(user);

  try {
    const config = useRuntimeConfig();
    const token = await user.getIdToken();
    const profile = await $fetch<{ role_id: string | null }>("/users/me", {
      baseURL: config.public.apiBase,
      headers: { Authorization: `Bearer ${token}` },
    });

    if (profile.role_id !== tokenRoleId) {
      await user.getIdToken(true);
      return profile.role_id;
    }
  } catch {
    // Backend unavailable: fall back to the token's role_id.
  }

  return tokenRoleId;
}
