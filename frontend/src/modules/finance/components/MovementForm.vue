<script setup lang="ts">
import { createMovement, getMovement, updateMovement, type MovementType, type PaymentMethod } from "~/modules/finance/api";
import { euroToCents } from "~/core/utils/currency";

const props = defineProps<{ movementId?: string }>();

const { t } = useI18n();
const router = useRouter();

const loading = ref(false);
const saving = ref(false);
const errorMessage = ref("");

const type = ref<MovementType>("expense");
const method = ref<PaymentMethod>("cash");
const amount = ref<number | null>(null);
const description = ref("");
const date = ref(new Date().toISOString().slice(0, 10));

const isEdit = computed(() => !!props.movementId);

const typeOptions = computed(() => [
  { label: t("finance.types.expense"), value: "expense" as MovementType },
  { label: t("finance.types.income"), value: "income" as MovementType },
  { label: t("finance.types.adjustment"), value: "adjustment" as MovementType },
]);

const methodOptions = computed(() => [
  { label: t("finance.methods.cash"), value: "cash" as PaymentMethod },
  { label: t("finance.methods.card"), value: "card" as PaymentMethod },
]);

watch(type, () => {
  amount.value = null;
  if (type.value !== "expense") {
    method.value = "cash";
  }
});

async function loadExisting() {
  if (!props.movementId) return;
  loading.value = true;
  try {
    const movement = await getMovement(props.movementId);
    type.value = movement.type;
    method.value = movement.method ?? "cash";
    amount.value = movement.amount_cents / 100;
    description.value = movement.description;
    date.value = movement.date;
  } catch (error) {
    errorMessage.value = t("finance.form.saveError");
  } finally {
    loading.value = false;
  }
}

async function handleSubmit() {
  if (amount.value === null || !description.value) return;

  saving.value = true;
  errorMessage.value = "";
  try {
    const payload = {
      type: type.value,
      method: type.value === "expense" ? method.value : null,
      amount_cents: euroToCents(amount.value),
      description: description.value,
      date: date.value,
    };

    if (isEdit.value && props.movementId) {
      await updateMovement(props.movementId, payload);
    } else {
      await createMovement(payload);
    }
    await router.push("/finance/transactions");
  } catch (error) {
    errorMessage.value = t("finance.form.saveError");
  } finally {
    saving.value = false;
  }
}

onMounted(loadExisting);
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">
      {{ isEdit ? t("finance.form.editTitle") : t("finance.form.newTitle") }}
    </h1>

    <div class="mt-6 max-w-md space-y-4">
      <SelectButton v-model="type" :options="typeOptions" option-label="label" option-value="value" />

      <SelectButton
        v-if="type === 'expense'"
        v-model="method"
        :options="methodOptions"
        option-label="label"
        option-value="value"
      />

      <div>
        <label class="mb-1 block text-sm text-slate-600">{{ t("finance.fields.amount") }}</label>
        <InputNumber
          v-model="amount"
          mode="currency"
          currency="EUR"
          locale="es-ES"
          :min="type === 'adjustment' ? undefined : 0"
          class="w-full"
        />
      </div>

      <div>
        <label class="mb-1 block text-sm text-slate-600">{{ t("finance.fields.description") }}</label>
        <InputText v-model="description" class="w-full" />
      </div>

      <div>
        <label class="mb-1 block text-sm text-slate-600">{{ t("finance.fields.date") }}</label>
        <input v-model="date" type="date" class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
      </div>

      <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

      <div class="flex gap-2">
        <Button :label="t('finance.form.save')" :loading="saving" @click="handleSubmit" />
        <Button :label="t('finance.form.cancel')" severity="secondary" text @click="router.back()" />
      </div>
    </div>
  </div>
</template>
