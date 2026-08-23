<script setup lang="ts">
import { createCategory, deleteCategory, listCategories, updateCategory, type Category } from "~/modules/finance/api";
import { usePermissionsStore } from "~/core/stores/permissions";
import Button from "~/core/components/ui/Button.vue";
import Card from "~/core/components/ui/Card.vue";
import ColorPicker from "~/core/components/ui/ColorPicker.vue";
import FormField from "~/core/components/ui/FormField.vue";
import FormInput from "~/core/components/ui/FormInput.vue";
import TableIconAction from "~/core/components/ui/TableIconAction.vue";
import { tableCellClass, tableHeaderCellClass, tableRowClass } from "~/core/ui/tableClasses";
import { DEFAULT_CATEGORY_COLOR, CATEGORY_COLOR_CLASSES, type CategoryColor } from "~/core/ui/categoryColors";

const permissionsStore = usePermissionsStore();
const { t } = useI18n();

if (!permissionsStore.has("CASHBOX_MANAGE")) {
  await navigateTo("/home");
}

useHead({ title: t("finance.categories.title") });

const categories = ref<Category[]>([]);
const loading = ref(true);
const errorMessage = ref("");

const newName = ref("");
const newColor = ref<CategoryColor>(DEFAULT_CATEGORY_COLOR);
const savingNew = ref(false);

const editingId = ref<string | null>(null);
const editingName = ref("");
const editingColor = ref<CategoryColor>(DEFAULT_CATEGORY_COLOR);

async function load() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await listCategories();
    categories.value = response.categories;
  } catch (error) {
    errorMessage.value = t("finance.categories.loadError");
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
    await createCategory({ name, color: newColor.value });
    newName.value = "";
    newColor.value = DEFAULT_CATEGORY_COLOR;
    await load();
  } catch (error) {
    errorMessage.value = t("finance.categories.saveError");
  } finally {
    savingNew.value = false;
  }
}

function startEdit(category: Category) {
  editingId.value = category.id;
  editingName.value = category.name;
  editingColor.value = category.color;
}

function cancelEdit() {
  editingId.value = null;
  editingName.value = "";
}

async function handleEditSave(category: Category) {
  const name = editingName.value.trim();
  if (!name) return;

  errorMessage.value = "";
  try {
    await updateCategory(category.id, { name, color: editingColor.value });
    cancelEdit();
    await load();
  } catch (error) {
    errorMessage.value = t("finance.categories.saveError");
  }
}

async function handleDelete(category: Category) {
  if (!confirm(t("finance.categories.confirmDelete", { name: category.name }))) return;
  try {
    await deleteCategory(category.id);
    await load();
  } catch (error) {
    errorMessage.value = t("finance.categories.deleteError");
  }
}

onMounted(load);
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">{{ t("finance.categories.title") }}</h1>

    <Card class="mt-6 max-w-xl space-y-4 p-6">
      <form class="flex items-end gap-2" @submit.prevent="handleCreate">
        <FormField :label="t('finance.categories.name')" input-id="category-name" class="flex-1">
          <FormInput id="category-name" v-model="newName" type="text" />
        </FormField>
        <Button type="submit" icon="lucide:plus" :loading="savingNew">
          {{ t("finance.categories.add") }}
        </Button>
      </form>

      <FormField :label="t('finance.categories.color')">
        <ColorPicker v-model="newColor" :aria-label="t('finance.categories.color')" />
      </FormField>
    </Card>

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <Card class="mt-4 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="bg-slate-50">
              <th :class="tableHeaderCellClass">{{ t("finance.categories.name") }}</th>
              <th :class="[tableHeaderCellClass, 'text-right']">{{ t("finance.categories.actions") }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="2" class="px-4 py-6 text-center text-slate-500">{{ t("finance.loading") }}</td>
            </tr>
            <tr v-else-if="categories.length === 0">
              <td colspan="2" class="px-4 py-6 text-center text-slate-500">{{ t("finance.categories.empty") }}</td>
            </tr>
            <tr v-for="category in categories" :key="category.id" :class="tableRowClass">
              <td :class="tableCellClass">
                <div v-if="editingId === category.id" class="flex items-center gap-3">
                  <FormInput v-model="editingName" type="text" :aria-label="t('finance.categories.name')" />
                  <ColorPicker v-model="editingColor" :aria-label="t('finance.categories.color')" />
                </div>
                <div v-else class="flex items-center gap-2">
                  <span class="h-2.5 w-2.5 rounded-full" :class="CATEGORY_COLOR_CLASSES[category.color].swatch" />
                  {{ category.name }}
                </div>
              </td>
              <td :class="[tableCellClass, 'text-right']">
                <div class="flex items-center justify-end gap-3">
                  <template v-if="editingId === category.id">
                    <TableIconAction
                      icon="lucide:check"
                      :label="t('finance.categories.save')"
                      tone="success"
                      @click="handleEditSave(category)"
                    />
                    <TableIconAction icon="lucide:x" :label="t('finance.categories.cancel')" @click="cancelEdit" />
                  </template>
                  <template v-else>
                    <TableIconAction
                      icon="lucide:pencil"
                      :label="t('finance.categories.edit')"
                      @click="startEdit(category)"
                    />
                    <TableIconAction
                      icon="lucide:trash-2"
                      :label="t('finance.categories.delete')"
                      tone="danger"
                      @click="handleDelete(category)"
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
