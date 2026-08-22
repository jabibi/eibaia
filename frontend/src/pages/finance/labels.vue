<script setup lang="ts">
import { createLabel, deleteLabel, listLabels, updateLabel, type Label } from "~/modules/finance/api";
import { usePermissionsStore } from "~/core/stores/permissions";
import Button from "~/core/components/ui/Button.vue";
import Card from "~/core/components/ui/Card.vue";
import ColorPicker from "~/core/components/ui/ColorPicker.vue";
import FormField from "~/core/components/ui/FormField.vue";
import FormInput from "~/core/components/ui/FormInput.vue";
import TableIconAction from "~/core/components/ui/TableIconAction.vue";
import { tableCellClass, tableHeaderCellClass, tableRowClass } from "~/core/ui/tableClasses";
import { DEFAULT_LABEL_COLOR, LABEL_COLOR_CLASSES, type LabelColor } from "~/core/ui/labelColors";

const permissionsStore = usePermissionsStore();
const { t } = useI18n();

if (!permissionsStore.has("CASHBOX_MANAGE")) {
  await navigateTo("/home");
}

useHead({ title: t("finance.labels.title") });

const labels = ref<Label[]>([]);
const loading = ref(true);
const errorMessage = ref("");

const newName = ref("");
const newColor = ref<LabelColor>(DEFAULT_LABEL_COLOR);
const savingNew = ref(false);

const editingId = ref<string | null>(null);
const editingName = ref("");
const editingColor = ref<LabelColor>(DEFAULT_LABEL_COLOR);

async function load() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await listLabels();
    labels.value = response.labels;
  } catch (error) {
    errorMessage.value = t("finance.labels.loadError");
  } finally {
    loading.value = false;
  }
}

async function handleCreate() {
  const name = newName.value.trim();
  if (!name) return;

  savingNew.value = true;
  errorMessage.value = "";
  try {
    await createLabel({ name, color: newColor.value });
    newName.value = "";
    newColor.value = DEFAULT_LABEL_COLOR;
    await load();
  } catch (error) {
    errorMessage.value = t("finance.labels.saveError");
  } finally {
    savingNew.value = false;
  }
}

function startEdit(label: Label) {
  editingId.value = label.id;
  editingName.value = label.name;
  editingColor.value = label.color;
}

function cancelEdit() {
  editingId.value = null;
  editingName.value = "";
}

async function handleEditSave(label: Label) {
  const name = editingName.value.trim();
  if (!name) return;

  errorMessage.value = "";
  try {
    await updateLabel(label.id, { name, color: editingColor.value });
    cancelEdit();
    await load();
  } catch (error) {
    errorMessage.value = t("finance.labels.saveError");
  }
}

async function handleDelete(label: Label) {
  if (!confirm(t("finance.labels.confirmDelete", { name: label.name }))) return;
  try {
    await deleteLabel(label.id);
    await load();
  } catch (error) {
    errorMessage.value = t("finance.labels.deleteError");
  }
}

onMounted(load);
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">{{ t("finance.labels.title") }}</h1>

    <Card class="mt-6 max-w-xl space-y-4 p-6">
      <form class="flex items-end gap-2" @submit.prevent="handleCreate">
        <FormField :label="t('finance.labels.name')" input-id="label-name" class="flex-1">
          <FormInput id="label-name" v-model="newName" type="text" />
        </FormField>
        <Button type="submit" icon="lucide:plus" :loading="savingNew">
          {{ t("finance.labels.add") }}
        </Button>
      </form>

      <FormField :label="t('finance.labels.color')">
        <ColorPicker v-model="newColor" :aria-label="t('finance.labels.color')" />
      </FormField>
    </Card>

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <Card class="mt-4 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="bg-slate-50">
              <th :class="tableHeaderCellClass">{{ t("finance.labels.name") }}</th>
              <th :class="[tableHeaderCellClass, 'text-right']">{{ t("finance.labels.actions") }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="2" class="px-4 py-6 text-center text-slate-500">{{ t("finance.loading") }}</td>
            </tr>
            <tr v-else-if="labels.length === 0">
              <td colspan="2" class="px-4 py-6 text-center text-slate-500">{{ t("finance.labels.empty") }}</td>
            </tr>
            <tr v-for="label in labels" :key="label.id" :class="tableRowClass">
              <td :class="tableCellClass">
                <div v-if="editingId === label.id" class="flex items-center gap-3">
                  <FormInput v-model="editingName" type="text" :aria-label="t('finance.labels.name')" />
                  <ColorPicker v-model="editingColor" :aria-label="t('finance.labels.color')" />
                </div>
                <div v-else class="flex items-center gap-2">
                  <span class="h-2.5 w-2.5 rounded-full" :class="LABEL_COLOR_CLASSES[label.color].swatch" />
                  {{ label.name }}
                </div>
              </td>
              <td :class="[tableCellClass, 'text-right']">
                <div class="flex items-center justify-end gap-3">
                  <template v-if="editingId === label.id">
                    <TableIconAction
                      icon="lucide:check"
                      :label="t('finance.labels.save')"
                      tone="success"
                      @click="handleEditSave(label)"
                    />
                    <TableIconAction icon="lucide:x" :label="t('finance.labels.cancel')" @click="cancelEdit" />
                  </template>
                  <template v-else>
                    <TableIconAction icon="lucide:pencil" :label="t('finance.labels.edit')" @click="startEdit(label)" />
                    <TableIconAction
                      icon="lucide:trash-2"
                      :label="t('finance.labels.delete')"
                      tone="danger"
                      @click="handleDelete(label)"
                    />
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  </div>
</template>
