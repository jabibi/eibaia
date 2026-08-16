<script setup lang="ts">
import { deleteMovement, updateMovementStatus, type Movement } from "~/modules/finance/api";
import { formatCurrency } from "~/core/utils/currency";
import { useAuthStore } from "~/core/stores/auth";
import { usePermissionsStore } from "~/core/stores/permissions";

const props = withDefaults(
  defineProps<{ movements: Movement[]; loading?: boolean; showActions?: boolean; emptyMessage?: string }>(),
  {
    loading: false,
    showActions: false,
    emptyMessage: undefined,
  },
);

const emit = defineEmits<{ (e: "refresh"): void }>();

const { t } = useI18n();
const authStore = useAuthStore();
const permissionsStore = usePermissionsStore();

/** Signed amount for display: expenses are always negative regardless of payment
 * method, even though card expenses don't move the cash safe balance. */
function displayCents(movement: Movement): number {
  return movement.type === "expense" ? -movement.amount_cents : movement.amount_cents;
}

function statusSeverity(status: Movement["status"]) {
  return status === "confirmed" ? "success" : "warning";
}

function isMutable(movement: Movement): boolean {
  if (permissionsStore.has("CASHBOX_MANAGE")) return true;
  return movement.created_by === authStore.user?.uid && movement.status === "draft";
}

function canEdit(movement: Movement): boolean {
  return isMutable(movement);
}

function canDelete(movement: Movement): boolean {
  return isMutable(movement);
}

function canConfirm(movement: Movement): boolean {
  return permissionsStore.has("CASHBOX_MANAGE") && movement.status === "draft";
}

async function handleDelete(movement: Movement) {
  if (!confirm(t("finance.actions.confirmDelete", { description: movement.description }))) return;
  try {
    await deleteMovement(movement.id);
    emit("refresh");
  } catch (error) {
    alert(t("finance.actions.deleteError"));
  }
}

async function handleConfirm(movement: Movement) {
  try {
    await updateMovementStatus(movement.id, "confirmed");
    emit("refresh");
  } catch (error) {
    alert(t("finance.actions.confirmError"));
  }
}
</script>

<template>
  <DataTable :value="movements" :loading="loading" data-key="id" class="mt-4">
    <template #empty>{{ props.emptyMessage ?? t("finance.noMovements") }}</template>

    <Column field="date" :header="t('finance.fields.date')" />
    <Column field="description" :header="t('finance.fields.description')" />
    <Column :header="t('finance.fields.type')">
      <template #body="{ data }">
        {{ t(`finance.types.${data.type}`) }}
        <span v-if="data.method">· {{ t(`finance.methods.${data.method}`) }}</span>
      </template>
    </Column>
    <Column :header="t('finance.fields.amount')">
      <template #body="{ data }">
        <span
          :class="
            displayCents(data) < 0 ? 'text-red-600' : displayCents(data) > 0 ? 'text-emerald-600' : 'text-slate-500'
          "
        >
          {{ formatCurrency(displayCents(data)) }}
        </span>
      </template>
    </Column>
    <Column :header="t('finance.fields.status')">
      <template #body="{ data }">
        <Tag :severity="statusSeverity(data.status)" :value="t(`finance.statuses.${data.status}`)" />
      </template>
    </Column>
    <Column v-if="showActions" :header="t('finance.fields.actions')">
      <template #body="{ data }">
        <div class="flex items-center gap-3">
          <NuxtLink
            v-if="canEdit(data)"
            :to="`/finance/${data.id}`"
            :title="t('finance.actions.edit')"
            class="text-slate-500 hover:text-emerald-700"
          >
            <i class="pi pi-pencil" />
          </NuxtLink>
          <button
            v-if="canConfirm(data)"
            type="button"
            :title="t('finance.actions.confirmMovement')"
            class="text-emerald-600 hover:text-emerald-800"
            @click="handleConfirm(data)"
          >
            <i class="pi pi-check-circle" />
          </button>
          <button
            v-if="canDelete(data)"
            type="button"
            :title="t('finance.actions.delete')"
            class="text-red-500 hover:text-red-700"
            @click="handleDelete(data)"
          >
            <i class="pi pi-times" />
          </button>
        </div>
      </template>
    </Column>
  </DataTable>
</template>
