import { defineStore } from "pinia";
import { listCashboxes, type Cashbox } from "~/modules/finance/api";

// Se asume una única caja compartida por todos los usuarios y movimientos (ver
// CLAUDE.md / conversación de diseño) — este store cachea ese único registro en
// localStorage para no tener que pedirlo a cada página que lo necesite (KPI,
// formulario de movimiento, el ribbon de entorno) y para que esté disponible
// incluso antes de que esa página monte su propio fetch.
const STORAGE_KEY = "elosue:cashbox-cache";
const MAX_AGE_MS = 24 * 60 * 60 * 1000; // 1 día — "una vez al día sería suficiente"

interface CashboxCacheEntry {
  cashbox: Cashbox;
  fetchedAt: number;
}

function readCache(): CashboxCacheEntry | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as CashboxCacheEntry) : null;
  } catch {
    return null;
  }
}

function writeCache(entry: CashboxCacheEntry | null) {
  try {
    if (entry) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(entry));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  } catch {
    // localStorage puede no estar disponible (modo privado, cuota llena) — el store
    // sigue funcionando en memoria, solo se pierde la persistencia entre recargas.
  }
}

interface CashboxState {
  cashbox: Cashbox | null;
  ready: boolean;
}

export const useCashboxStore = defineStore("cashbox", {
  state: (): CashboxState => ({
    cashbox: null,
    ready: false,
  }),

  actions: {
    /** Llamado en cada login/init: solo pide la caja a la API si el registro en
     * caché no existe o supera el día de antigüedad (expire_date). */
    async load() {
      const cached = readCache();
      const isFresh = !!cached && Date.now() - cached.fetchedAt < MAX_AGE_MS;
      if (isFresh) {
        this.cashbox = cached.cashbox;
        this.ready = true;
        return;
      }
      await this.refresh();
    },

    async refresh() {
      try {
        const { cashboxes } = await listCashboxes();
        this.cashbox = cashboxes[0] ?? null;
        writeCache(this.cashbox ? { cashbox: this.cashbox, fetchedAt: Date.now() } : null);
      } catch {
        // Sin red/permiso: mantiene lo que ya hubiera en caché en vez de dejar la app sin caja.
        this.cashbox = readCache()?.cashbox ?? null;
      } finally {
        this.ready = true;
      }
    },

    clear() {
      this.cashbox = null;
      this.ready = false;
      writeCache(null);
    },
  },
});
