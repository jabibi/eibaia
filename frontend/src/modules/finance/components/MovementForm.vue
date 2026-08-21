<script setup lang="ts">
import {
  createMovement,
  getMovement,
  listCashboxes,
  listLabels,
  updateMovement,
  type Cashbox,
  type Label,
  type MovementType,
  type PaymentMethod,
} from "~/modules/finance/api";
import { euroToCents } from "~/core/utils/currency";
import Button from "~/core/components/ui/Button.vue";
import Card from "~/core/components/ui/Card.vue";
import ColorSelect from "~/core/components/ui/ColorSelect.vue";
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
const cashboxes = ref<Cashbox[]>([]);
const cashboxId = ref("");
const labels = ref<Label[]>([]);
const labelId = ref("");
const amount = ref("");
const description = ref("");
const date = ref(new Date().toISOString().slice(0, 10));

const isEdit = computed(() => !!props.movementId);

useHead({ title: computed(() => (isEdit.value ? t("finance.form.editTitle") : t("finance.form.newTitle"))) });

const typeOptions = computed(() => [
  { label: t("finance.types.expense"), value: "expense" as MovementType },
  { label: t("finance.types.income"), value: "income" as MovementType },
]);

const methodOptions = computed(() => [
  { label: t("finance.methods.cash"), value: "cash" as PaymentMethod },
  { label: t("finance.methods.card"), value: "card" as PaymentMethod },
]);

watch(type, () => {
  amount.value = "";
});

const selectedCashbox = computed(() => cashboxes.value.find((cashbox) => cashbox.id === cashboxId.value) ?? null);

const labelOptions = computed(() =>
  labels.value.map((label) => ({ value: label.id, label: label.name, color: label.color })),
);

async function loadExisting() {
  if (!props.movementId) return;
  loading.value = true;
  try {
    const movement = await getMovement(props.movementId);
    type.value = movement.type;
    method.value = movement.method ?? "cash";
    cashboxId.value = movement.cashbox_id ?? "";
    labelId.value = movement.label_id ?? "";
    amount.value = String(movement.amount_cents / 100);
    description.value = movement.description;
    date.value = movement.date;
  } catch (error) {
    errorMessage.value = t("finance.form.saveError");
  } finally {
    loading.value = false;
  }
}

async function loadCashboxes() {
  const { cashboxes: list } = await listCashboxes();
  cashboxes.value = list;
  const [first] = list;
  if (!props.movementId && !cashboxId.value && first) {
    cashboxId.value = first.id;
  }
}

async function loadLabels() {
  const { labels: list } = await listLabels();
  labels.value = list;
  const [first] = list;
  if (!props.movementId && !labelId.value && first) {
    labelId.value = first.id;
  }
}

async function handleSubmit() {
  const amountValue = Number(amount.value);
  if (!amount.value || Number.isNaN(amountValue) || !description.value || !labelId.value) return;

  saving.value = true;
  errorMessage.value = "";
  try {
    const payload = {
      type: type.value,
      method: method.value,
      cashbox_id: method.value === "cash" ? cashboxId.value || null : null,
      label_id: labelId.value,
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
  loadCashboxes();
  loadLabels();
  loadExisting();
});
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">
      {{ isEdit ? t("finance.form.editTitle") : t("finance.form.newTitle") }}
    </h1>

    <Card class="relative mt-6 max-w-xl space-y-5 p-6">
      <span
        v-if="method === 'cash' && selectedCashbox"
        class="absolute -right-2 -top-2 flex items-center gap-1 rounded-full bg-indigo-600 px-3 py-1 text-xs font-medium text-white shadow-sm"
      >
        <Icon name="lucide:vault" />
        {{ selectedCashbox.name }}
      </span>

      <SegmentedControl v-model="type" :options="typeOptions" />

      <SegmentedControl v-model="method" :options="methodOptions" />

      <FormField :label="t('finance.fields.label')">
        <ColorSelect v-model="labelId" :options="labelOptions" />
      </FormField>

      <FormField :label="t('finance.fields.amount')">
        <FormInput v-model="amount" type="number" step="0.01" :min="0" />
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
