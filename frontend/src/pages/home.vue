<script setup lang="ts">
import type { Component } from "vue";
import { useAuthStore } from "~/core/stores/auth";
import { usePermissionsStore } from "~/core/stores/permissions";
import { useDashboardPreferencesStore } from "~/core/stores/dashboardPreferences";
import { KPI_REGISTRY } from "~/core/config/kpis";
import KpiCard from "~/core/components/ui/KpiCard.vue";
import { KPI_COMPONENTS, loadKpiProps } from "~/core/components/kpis";

const authStore = useAuthStore();
const permissionsStore = usePermissionsStore();
const dashboardPreferences = useDashboardPreferencesStore();
const { t } = useI18n();

useHead({ title: t("sidebar.home") });

const isEditing = ref(false);
const loading = ref(true);
const errorMessage = ref("");
const kpiProps = ref<Record<string, Record<string, unknown>>>({});

// Solo se puede desanclar (quitar/reordenar) desde /home; fijar/desfijar es cosa del
// módulo de origen (ver KpiCard "showStar") para evitar el click accidental que pide el
// encargo. El conjunto de KPIs visibles aquí solo puede reducirse durante la visita (vía
// removeKpi), nunca crecer, así que no hace falta re-cargar datos tras la carga inicial.
const visibleKpis = computed(() =>
  dashboardPreferences.orderedIds
    .map((id) => KPI_REGISTRY.find((kpi) => kpi.id === id))
    .filter((kpi) => !!kpi && (!kpi.permission || permissionsStore.has(kpi.permission))),
);

interface ResolvedKpi {
  id: string;
  to: string;
  variant?: "warning" | "danger";
  component: Component;
  props: Record<string, unknown>;
}

// /home no sabe qué datos necesita cada KPI ni de dónde vienen — solo pide sus props por id
// (ver core/components/kpis: loadKpiProps) y las reenvía tal cual a su componente.
const resolvedKpis = computed<ResolvedKpi[]>(() =>
  visibleKpis.value.flatMap((kpi): ResolvedKpi[] => {
    const entry = kpi && KPI_COMPONENTS[kpi.id];
    if (!kpi || !entry) return [];
    return [
      {
        id: kpi.id,
        to: kpi.to,
        variant: kpi.variant,
        component: entry.component,
        props: { ...kpiProps.value[kpi.id], loading: loading.value },
      },
    ];
  }),
);

async function load() {
  const ids = visibleKpis.value.map((kpi) => kpi!.id);
  if (ids.length === 0) {
    loading.value = false;
    return;
  }

  loading.value = true;
  errorMessage.value = "";
  try {
    kpiProps.value = await loadKpiProps(ids);
  } catch (error) {
    errorMessage.value = t("home.loadError");
  } finally {
    loading.value = false;
  }
}

function toggleEditing() {
  isEditing.value = !isEditing.value;
}

function moveLeft(index: number) {
  if (index === 0) return;
  const ids = dashboardPreferences.orderedIds;
  const temp = ids[index - 1]!;
  ids[index - 1] = ids[index]!;
  ids[index] = temp;
  dashboardPreferences.reorder(ids);
}

function moveRight(index: number) {
  const ids = dashboardPreferences.orderedIds;
  if (index === ids.length - 1) return;
  const temp = ids[index]!;
  ids[index] = ids[index + 1]!;
  ids[index + 1] = temp;
  dashboardPreferences.reorder(ids);
}

function removeKpi(kpiId: string) {
  dashboardPreferences.remove(kpiId);
}

onMounted(load);
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between gap-3">
      <h1 class="min-w-0 truncate text-2xl font-semibold text-slate-800">
        {{ t("home.greeting", { name: authStore.user?.displayName ?? "" }) }}
      </h1>
      <button
        v-if="dashboardPreferences.pinnedKpis.length > 0"
        type="button"
        :aria-label="isEditing ? t('home.saveDashboard') : t('home.editDashboard')"
        :title="isEditing ? t('home.saveDashboard') : t('home.editDashboard')"
        class="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border shadow-sm transition-all active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
        :class="
          isEditing
            ? 'border-indigo-600 bg-indigo-600 text-white hover:bg-indigo-700'
            : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900'
        "
        @click="toggleEditing"
      >
        <Icon :name="isEditing ? 'lucide:check' : 'lucide:pencil'" class="h-5 w-5 transition-transform" />
        <span class="sr-only">{{ isEditing ? t("home.saveDashboard") : t("home.editDashboard") }}</span>
      </button>
    </div>

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <p v-if="dashboardPreferences.ready && resolvedKpis.length === 0" class="mt-6 text-sm text-slate-500">
      {{ t("home.empty") }}
    </p>

    <div class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <template v-for="(kpi, index) in resolvedKpis" :key="kpi.id">
        <KpiCard v-if="!isEditing" :to="kpi.to" :variant="kpi.variant" :kpi-id="kpi.id" :show-star="false">
          <component :is="kpi.component" v-bind="kpi.props" />
        </KpiCard>

        <div
          v-else
          class="group relative flex h-full flex-col rounded-lg border-2 border-dashed border-slate-300 bg-white p-6"
        >
          <button
            type="button"
            class="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 text-slate-400 transition-colors hover:border-red-200 hover:bg-red-50 hover:text-red-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            :aria-label="t('home.removeKpi')"
            @click="removeKpi(kpi.id)"
          >
            <Icon name="lucide:x" />
          </button>
          <component :is="kpi.component" v-bind="kpi.props" />
          <div class="mt-auto flex justify-center pt-4">
            <div class="inline-flex divide-x divide-slate-200 overflow-hidden rounded-full border border-slate-200">
              <button
                type="button"
                class="flex h-8 w-10 items-center justify-center text-slate-500 transition-colors hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-indigo-500 disabled:cursor-not-allowed disabled:opacity-30"
                :disabled="index === 0"
                :aria-label="t('home.moveLeft')"
                @click="moveLeft(index)"
              >
                <Icon name="lucide:arrow-left" />
              </button>
              <button
                type="button"
                class="flex h-8 w-10 items-center justify-center text-slate-500 transition-colors hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-indigo-500 disabled:cursor-not-allowed disabled:opacity-30"
                :disabled="index === resolvedKpis.length - 1"
                :aria-label="t('home.moveRight')"
                @click="moveRight(index)"
              >
                <Icon name="lucide:arrow-right" />
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
