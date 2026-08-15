import { defineStore } from "pinia";
import {
  type User,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
} from "firebase/auth";

export type Role = "admin" | "manager" | "user";

interface AuthState {
  user: User | null;
  role: Role | null;
  ready: boolean;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    user: null,
    role: null,
    ready: false,
  }),

  getters: {
    isAuthenticated: (state) => state.user !== null,
    isApproved: (state) => state.role !== null,
    isAdmin: (state) => state.role === "admin",
    isManager: (state) => state.role === "admin" || state.role === "manager",
  },

  actions: {
    async init() {
      const { $firebaseAuth } = useNuxtApp();

      return new Promise<void>((resolve) => {
        onAuthStateChanged($firebaseAuth, async (user) => {
          this.user = user;
          this.role = user ? await syncRole(user) : null;
          this.ready = true;
          resolve();
        });
      });
    },

    async loginWithGoogle() {
      const { $firebaseAuth, $googleProvider } = useNuxtApp();
      const { user } = await signInWithPopup($firebaseAuth, $googleProvider);
      this.user = user;
      this.role = await syncRole(user);
    },

    async logout() {
      const { $firebaseAuth } = useNuxtApp();
      await signOut($firebaseAuth);
      this.user = null;
      this.role = null;
    },

    async getIdToken(forceRefresh = false) {
      return this.user?.getIdToken(forceRefresh) ?? null;
    },
  },
});

async function resolveRole(user: User): Promise<Role | null> {
  const { claims } = await user.getIdTokenResult();
  return (claims.role as Role) ?? null;
}

/**
 * Resolves the role from the token and cross-checks it against the backend, which may
 * promote the first-ever registered user to admin (see ensure_first_admin). If the backend
 * returns a different role, forces an ID token refresh. A `null` role means no role has been
 * assigned yet (no access).
 */
async function syncRole(user: User): Promise<Role | null> {
  const tokenRole = await resolveRole(user);

  try {
    const config = useRuntimeConfig();
    const token = await user.getIdToken();
    const profile = await $fetch<{ role: Role | null }>("/users/me", {
      baseURL: config.public.apiBase,
      headers: { Authorization: `Bearer ${token}` },
    });

    if (profile.role !== tokenRole) {
      await user.getIdToken(true);
      return profile.role;
    }
  } catch {
    // Backend unavailable: fall back to the token's role.
  }

  return tokenRole;
}
