import { defineStore } from "pinia";
import {
  type User,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
} from "firebase/auth";
import { usePermissionsStore } from "~/core/stores/permissions";
import { useDashboardPreferencesStore } from "~/core/stores/dashboardPreferences";

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
            await useDashboardPreferencesStore().load();
          } else {
            usePermissionsStore().clear();
            useDashboardPreferencesStore().clear();
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
      await useDashboardPreferencesStore().load();
    },

    /**
     * Re-checks role_id against the backend without waiting for a Firebase auth-state
     * change (which only fires on sign-in/out, never when an admin grants a role while
     * the user is already signed in). Used by pending.vue to notice an approval that
     * happened while the tab/PWA was backgrounded, without requiring a hard reload.
     */
    async refreshRoleId() {
      if (!this.user) return;
      this.roleId = await syncRoleId(this.user);
      if (this.roleId) {
        await usePermissionsStore().load();
      }
    },

    async logout() {
      const { $firebaseAuth } = useNuxtApp();
      await signOut($firebaseAuth);
      usePermissionsStore().clear();
      useDashboardPreferencesStore().clear();
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
