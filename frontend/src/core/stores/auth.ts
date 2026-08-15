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
  role: Role;
  ready: boolean;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    user: null,
    role: "user",
    ready: false,
  }),

  getters: {
    isAuthenticated: (state) => state.user !== null,
    isAdmin: (state) => state.role === "admin",
    isManager: (state) => state.role === "admin" || state.role === "manager",
  },

  actions: {
    async init() {
      const { $firebaseAuth } = useNuxtApp();

      return new Promise<void>((resolve) => {
        onAuthStateChanged($firebaseAuth, async (user) => {
          this.user = user;
          this.role = await resolveRole(user);
          this.ready = true;
          resolve();
        });
      });
    },

    async loginWithGoogle() {
      const { $firebaseAuth, $googleProvider } = useNuxtApp();
      const { user } = await signInWithPopup($firebaseAuth, $googleProvider);
      this.user = user;
      this.role = await resolveRole(user);
    },

    async logout() {
      const { $firebaseAuth } = useNuxtApp();
      await signOut($firebaseAuth);
      this.user = null;
      this.role = "user";
    },

    async getIdToken(forceRefresh = false) {
      return this.user?.getIdToken(forceRefresh) ?? null;
    },
  },
});

async function resolveRole(user: User | null): Promise<Role> {
  if (!user) return "user";
  const { claims } = await user.getIdTokenResult();
  return (claims.role as Role) ?? "user";
}
