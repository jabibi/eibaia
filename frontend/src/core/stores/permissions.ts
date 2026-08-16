import { defineStore } from "pinia";
import { apiFetch } from "~/core/api/http";

interface PermissionsState {
  codes: string[];
  ready: boolean;
}

export const usePermissionsStore = defineStore("permissions", {
  state: (): PermissionsState => ({
    codes: [],
    ready: false,
  }),

  getters: {
    has: (state) => (code: string) => state.codes.includes(code),
  },

  actions: {
    async load() {
      try {
        this.codes = await apiFetch<string[]>("/users/me/permissions");
      } catch {
        this.codes = [];
      } finally {
        this.ready = true;
      }
    },

    clear() {
      this.codes = [];
      this.ready = false;
    },
  },
});
