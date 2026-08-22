<script setup lang="ts">
import { deleteMovement, updateMovementStatus, type Label, type Movement } from "~/modules/finance/api";
import { formatCurrency } from "~/core/utils/currency";
import { useAuthStore } from "~/core/stores/auth";
import { usePermissionsStore } from "~/core/stores/permissions";
import Card from "~/core/components/ui/Card.vue";
import StatusBadge from "~/core/components/ui/StatusBadge.vue";
import TableIconAction from "~/core/components/ui/TableIconAction.vue";
import { tableCellClass, tableHeaderCellClass, tableRowClass } from "~/core/ui/tableClasses";
import { LABEL_COLOR_CLASSES } from "~/core/ui/labelColors";

const props = withDefaults(
  defineProps<{
    movements: Movement[];
    loading?: boolean;
    showActions?: boolean;
    emptyMessage?: string;
    labels?: Label[];
  }>(),
  {
    loading: false,
    showActions: false,
    emptyMessage: undefined,
    labels: () => [],
  },
);

const labelById = computed(() => new Map(props.labels.map((label) => [label.id, label])));

function labelFor(movement: Movement): Label | null {
  if (!movement.label_id) return null;
  return labelById.value.get(movement.label_id) ?? null;
}

function typeLine(movement: Movement): string {
  const parts = [t(`finance.types.${movement.type}`)];
  if (movement.method) parts.push(t(`finance.methods.${movement.method}`));
  return parts.join(" ");
}

const emit = defineEmits<{ (e: "refresh"): void }>();

const { t } = useI18n();
const authStore = useAuthStore();
const permissionsStore = usePermissionsStore();

/** Signed amount for display: expenses are always negative regardless of payment
 * method, even though card expenses don't move the cashbox's cash balance. */
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
            <th :class="tableHeaderCellClass">{{ t("finance.fields.label") }}</th>
            <th :class="tableHeaderCellClass">{{ t("finance.fields.amount") }}</th>
            <th :class="tableHeaderCellClass">{{ t("finance.fields.status") }}</th>
            <th v-if="showActions" :class="tableHeaderCellClass">{{ t("finance.fields.actions") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="showActions ? 7 : 6" class="px-4 py-6 text-center text-slate-500">
              {{ t("finance.loading") }}
            </td>
          </tr>
          <tr v-else-if="movements.length === 0">
            <td :colspan="showActions ? 7 : 6" class="px-4 py-6 text-center text-slate-500">
              {{ props.emptyMessage ?? t("finance.noMovements") }}
            </td>
          </tr>
          <tr v-for="movement in movements" :key="movement.id" :class="tableRowClass">
            <td :class="tableCellClass">{{ movement.date }}</td>
            <td :class="tableCellClass">{{ movement.description }}</td>
            <td :class="tableCellClass">{{ typeLine(movement) }}</td>
            <td :class="tableCellClass">
              <span
                v-if="labelFor(movement)"
                class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                :class="[LABEL_COLOR_CLASSES[labelFor(movement)!.color].chipBg, LABEL_COLOR_CLASSES[labelFor(movement)!.color].text]"
              >
                {{ labelFor(movement)!.name }}
              </span>
              <span v-else class="text-slate-400">—</span>
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
                <TableIconAction
                  v-if="canEdit(movement)"
                  :to="`/finance/${movement.id}`"
                  icon="lucide:pencil"
                  :label="t('finance.actions.edit')"
                />
                <TableIconAction
                  v-if="canConfirm(movement)"
                  icon="lucide:circle-check-big"
                  :label="t('finance.actions.confirmMovement')"
                  tone="success"
                  @click="handleConfirm(movement)"
                />
                <TableIconAction
                  v-if="canDelete(movement)"
                  icon="lucide:x"
                  :label="t('finance.actions.delete')"
                  tone="danger"
                  @click="handleDelete(movement)"
                />
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </Card>
</template>
