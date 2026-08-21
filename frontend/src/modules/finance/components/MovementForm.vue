<script setup lang="ts">
import { createMovement, getMovement, updateMovement, type MovementType, type PaymentMethod } from "~/modules/finance/api";
import { euroToCents } from "~/core/utils/currency";
import Button from "~/core/components/ui/Button.vue";
import Card from "~/core/components/ui/Card.vue";
import FormField from "~/core/components/ui/FormField.vue";
import FormInput from "~/core/components/ui/FormInput.vue";
import SegmentedControl from "~/core/components/ui/SegmentedControl.vue";

const props = defineProps<{ movementId?: string }>();

const { t } = useI18n();
const router = useRouter();
const route = useRoute();

const loading = ref(false);
const saving = ref(false);
const errorMessage = ref("");

const type = ref<MovementType>("expense");
const method = ref<PaymentMethod>("cash");
const amount = ref("");
const description = ref("");
const date = ref(new Date().toISOString().slice(0, 10));

const isEdit = computed(() => !!props.movementId);

useHead({ title: computed(() => (isEdit.value ? t("finance.form.editTitle") : t("finance.form.newTitle"))) });

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
  amount.value = "";
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
    amount.value = String(movement.amount_cents / 100);
    description.value = movement.description;
    date.value = movement.date;
  } catch (error) {
    errorMessage.value = t("finance.form.saveError");
  } finally {
    loading.value = false;
  }
}

async function handleSubmit() {
  const amountValue = Number(amount.value);
  if (!amount.value || Number.isNaN(amountValue) || !description.value) return;

  saving.value = true;
  errorMessage.value = "";
  try {
    const payload = {
      type: type.value,
      method: type.value === "expense" ? method.value : null,
      amount_cents: euroToCents(amountValue),
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

onMounted(() => {
  if (!props.movementId && route.query.type === "card") {
    method.value = "card";
  }
  loadExisting();
});
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">
      {{ isEdit ? t("finance.form.editTitle") : t("finance.form.newTitle") }}
    </h1>

    <Card class="mt-6 max-w-xl space-y-5 p-6">
      <SegmentedControl v-model="type" :options="typeOptions" />

      <SegmentedControl v-if="type === 'expense'" v-model="method" :options="methodOptions" />

      <FormField :label="t('finance.fields.amount')">
        <FormInput
          v-model="amount"
          type="number"
          step="0.01"
          :min="type === 'adjustment' ? undefined : 0"
        />
      </FormField>

      <FormField :label="t('finance.fields.description')">
        <FormInput v-model="description" type="text" />
      </FormField>

      <FormField :label="t('finance.fields.date')">
        <FormInput v-model="date" type="date" />
      </FormField>

      <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

      <div class="flex gap-2">
        <Button :disabled="saving" @click="handleSubmit">
          {{ saving ? "…" : t("finance.form.save") }}
        </Button>
        <Button variant="secondary" @click="router.back()">
          {{ t("finance.form.cancel") }}
        </Button>
      </div>
    </Card>
  </div>
</template>
