<script setup lang="ts">
import { deleteMovement, updateMovementStatus, type Movement } from "~/modules/finance/api";
import { formatCurrency } from "~/core/utils/currency";
import { useAuthStore } from "~/core/stores/auth";
import { usePermissionsStore } from "~/core/stores/permissions";
import Card from "~/core/components/ui/Card.vue";
import StatusBadge from "~/core/components/ui/StatusBadge.vue";
import { tableCellClass, tableHeaderCellClass, tableRowClass } from "~/core/ui/tableClasses";

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
  <Card class="mt-4 overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full text-left text-sm">
        <thead>
          <tr class="bg-slate-50">
            <th :class="tableHeaderCellClass">{{ t("finance.fields.date") }}</th>
            <th :class="tableHeaderCellClass">{{ t("finance.fields.description") }}</th>
            <th :class="tableHeaderCellClass">{{ t("finance.fields.type") }}</th>
            <th :class="tableHeaderCellClass">{{ t("finance.fields.amount") }}</th>
            <th :class="tableHeaderCellClass">{{ t("finance.fields.status") }}</th>
            <th v-if="showActions" :class="tableHeaderCellClass">{{ t("finance.fields.actions") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="showActions ? 6 : 5" class="px-4 py-6 text-center text-slate-400">
              {{ t("finance.loading") }}
            </td>
          </tr>
          <tr v-else-if="movements.length === 0">
            <td :colspan="showActions ? 6 : 5" class="px-4 py-6 text-center text-slate-400">
              {{ props.emptyMessage ?? t("finance.noMovements") }}
            </td>
          </tr>
          <tr v-for="movement in movements" :key="movement.id" :class="tableRowClass">
            <td :class="tableCellClass">{{ movement.date }}</td>
            <td :class="tableCellClass">{{ movement.description }}</td>
            <td :class="tableCellClass">
              {{ t(`finance.types.${movement.type}`) }}
              <span v-if="movement.method">· {{ t(`finance.methods.${movement.method}`) }}</span>
            </td>
            <td :class="tableCellClass">
              <span
                :class="
                  displayCents(movement) < 0
                    ? 'text-red-600'
                    : displayCents(movement) > 0
                      ? 'text-emerald-600'
                      : 'text-slate-500'
                "
              >
                {{ formatCurrency(displayCents(movement)) }}
              </span>
            </td>
            <td :class="tableCellClass">
              <StatusBadge
                :variant="statusSeverity(movement.status)"
                :label="t(`finance.statuses.${movement.status}`)"
              />
            </td>
            <td v-if="showActions" :class="tableCellClass">
              <div class="flex items-center gap-3">
                <NuxtLink
                  v-if="canEdit(movement)"
                  :to="`/finance/${movement.id}`"
                  :title="t('finance.actions.edit')"
                  class="text-slate-500 hover:text-emerald-700"
                >
                  <Icon name="lucide:pencil" />
                </NuxtLink>
                <button
                  v-if="canConfirm(movement)"
                  type="button"
                  :title="t('finance.actions.confirmMovement')"
                  class="text-emerald-600 hover:text-emerald-800"
                  @click="handleConfirm(movement)"
                >
                  <Icon name="lucide:circle-check-big" />
                </button>
                <button
                  v-if="canDelete(movement)"
                  type="button"
                  :title="t('finance.actions.delete')"
                  class="text-red-500 hover:text-red-700"
                  @click="handleDelete(movement)"
                >
                  <Icon name="lucide:x" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </Card>
</template>
