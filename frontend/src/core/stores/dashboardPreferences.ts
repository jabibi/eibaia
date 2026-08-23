import { defineStore } from "pinia";
import { getDashboardPreferences, updateDashboardPreferences, type PinnedKpi } from "~/modules/users/api";

interface DashboardPreferencesState {
  pinnedKpis: PinnedKpi[];
  ready: boolean;
}

// Serializes PUT calls so two rapid persist() calls (e.g. two quick arrow clicks) can't
// resolve out of order and let an older snapshot silently overwrite a newer one.
let persistChain: Promise<unknown> = Promise.resolve();

export const useDashboardPreferencesStore = defineStore("dashboardPreferences", {
  state: (): DashboardPreferencesState => ({
    pinnedKpis: [],
    ready: false,
  }),

  getters: {
    isPinned: (state) => (kpiId: string) => state.pinnedKpis.some((kpi) => kpi.id === kpiId),
    orderedIds: (state) => [...state.pinnedKpis].sort((a, b) => a.order - b.order).map((kpi) => kpi.id),
  },

  actions: {
    async load() {
      try {
        const prefs = await getDashboardPreferences();
        this.pinnedKpis = prefs.pinned_kpis;
      } catch {
        this.pinnedKpis = [];
      } finally {
        this.ready = true;
      }
    },

    async toggle(kpiId: string) {
      if (this.isPinned(kpiId)) {
        this.pinnedKpis = this.pinnedKpis.filter((kpi) => kpi.id !== kpiId);
      } else {
        this.pinnedKpis = [...this.pinnedKpis, { id: kpiId, order: this.pinnedKpis.length }];
      }
      await this.persist();
    },

    async remove(kpiId: string) {
      this.pinnedKpis = this.pinnedKpis.filter((kpi) => kpi.id !== kpiId);
      await this.persist();
    },

    async reorder(idsInNewOrder: string[]) {
      this.pinnedKpis = idsInNewOrder.map((id, order) => ({ id, order }));
      await this.persist();
    },

    async persist() {
      persistChain = persistChain.then(() => updateDashboardPreferences({ pinned_kpis: this.pinnedKpis }));
      await persistChain;
    },

    clear() {
      this.pinnedKpis = [];
      this.ready = false;
    },
  },
});
