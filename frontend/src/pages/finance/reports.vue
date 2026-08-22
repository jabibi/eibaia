<script setup lang="ts">
import { Workbook } from "exceljs";
import {
  getReport,
  listLabels,
  type Label,
  type Movement,
  type PaymentMethod,
  type ReportTotals,
} from "~/modules/finance/api";
import { formatCurrency } from "~/core/utils/currency";
import { currentMonthRange, previousMonthRange } from "~/core/utils/dateRange";
import { usePermissionsStore } from "~/core/stores/permissions";
import Button from "~/core/components/ui/Button.vue";
import Card from "~/core/components/ui/Card.vue";
import FormField from "~/core/components/ui/FormField.vue";
import FormInput from "~/core/components/ui/FormInput.vue";
import FormSelect from "~/core/components/ui/FormSelect.vue";
import { tableCellClass, tableHeaderCellClass, tableRowClass } from "~/core/ui/tableClasses";
import { LABEL_COLOR_CLASSES } from "~/core/ui/labelColors";

const permissionsStore = usePermissionsStore();

if (!permissionsStore.has("CASHBOX_MANAGE")) {
  await navigateTo("/home");
}

const { t } = useI18n();

useHead({ title: t("finance.reports.title") });

const initialRange = currentMonthRange();
const dateFrom = ref(initialRange.from);
const dateTo = ref(initialRange.to);
const scope = ref<PaymentMethod | "">("");
const labelId = ref("");

const labels = ref<Label[]>([]);
const movements = ref<Movement[]>([]);
const totals = ref<ReportTotals>({ income_cents: 0, expense_cents: 0, net_cents: 0 });
const loading = ref(true);
const errorMessage = ref("");

const labelById = computed(() => new Map(labels.value.map((label) => [label.id, label])));

function labelFor(movement: Movement): Label | null {
  if (!movement.label_id) return null;
  return labelById.value.get(movement.label_id) ?? null;
}

function movementLabelName(movement: Movement): string {
  return labelFor(movement)?.name ?? "—";
}

function typeLine(movement: Movement): string {
  const parts = [t(`finance.types.${movement.type}`)];
  if (movement.method) parts.push(t(`finance.methods.${movement.method}`));
  return parts.join(" ");
}

function displayCents(movement: Movement): number {
  return movement.type === "expense" ? -movement.amount_cents : movement.amount_cents;
}

const scopeLabel = computed(() =>
  scope.value ? t(`finance.methods.${scope.value}`) : t("finance.reports.filters.allTypes"),
);

const labelFilterLabel = computed(() => {
  if (!labelId.value) return t("finance.reports.filters.allLabels");
  return labelById.value.get(labelId.value)?.name ?? t("finance.reports.filters.allLabels");
});

async function loadLabels() {
  const response = await listLabels();
  labels.value = response.labels;
}

async function loadReport() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const result = await getReport({
      date_from: dateFrom.value,
      date_to: dateTo.value,
      scope: scope.value || undefined,
      label_id: labelId.value || undefined,
    });
    movements.value = result.movements;
    totals.value = result.totals;
  } catch (error) {
    errorMessage.value = t("finance.reports.loadError");
  } finally {
    loading.value = false;
  }
}

let debounceTimer: ReturnType<typeof setTimeout> | undefined;
watch([dateFrom, dateTo, scope, labelId], () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(loadReport, 300);
});

function setLastMonth() {
  const { from, to } = previousMonthRange();
  dateFrom.value = from;
  dateTo.value = to;
}

function setCurrentMonth() {
  const { from, to } = currentMonthRange();
  dateFrom.value = from;
  dateTo.value = to;
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

const CURRENCY_FORMAT = '#,##0.00" €"';
const HEADER_BG = "FF0F766E";
const HEADER_TEXT = "FFFFFFFF";
const FILTERS_TEXT = "FF64748B";
const TABLE_HEADER_BG = "FFF1F5F9";
const NEGATIVE_TEXT = "FFDC2626";
const POSITIVE_TEXT = "FF059669";
const AUTO_FIT_MIN_WIDTH = 10;
const AUTO_FIT_START_ROW = 4; // skips the merged title/filters banner rows (1-2)

async function exportExcel() {
  const workbook = new Workbook();
  const sheet = workbook.addWorksheet(t("finance.reports.export.sheetName"));

  sheet.mergeCells("A1:E1");
  const titleCell = sheet.getCell("A1");
  titleCell.value = t("finance.reports.export.docTitle").toUpperCase();
  titleCell.font = { name: "Arial", size: 14, bold: true, color: { argb: HEADER_TEXT } };
  titleCell.alignment = { horizontal: "center", vertical: "middle" };
  titleCell.fill = { type: "pattern", pattern: "solid", fgColor: { argb: HEADER_BG } };

  sheet.mergeCells("A2:E2");
  const filtersCell = sheet.getCell("A2");
  filtersCell.value = [
    t("finance.reports.export.periodLabel", { from: dateFrom.value, to: dateTo.value }),
    `${t("finance.reports.filters.type")}: ${scopeLabel.value}`,
    `${t("finance.reports.filters.label")}: ${labelFilterLabel.value}`,
  ].join(" | ");
  filtersCell.font = { italic: true, size: 10, color: { argb: FILTERS_TEXT } };

  sheet.mergeCells("A4:B4");
  sheet.getCell("A4").value = t("finance.reports.export.summaryTitle").toUpperCase();
  sheet.getCell("A4").font = { bold: true };

  sheet.getCell("A5").value = `${t("finance.reports.summary.income")}:`;
  sheet.getCell("D5").value = `${t("finance.reports.summary.net")}:`;
  sheet.getCell("A6").value = `${t("finance.reports.summary.expense")}:`;

  const kpiCells = [
    { ref: "B5", value: totals.value.income_cents / 100 },
    { ref: "E5", value: totals.value.net_cents / 100 },
    { ref: "B6", value: -totals.value.expense_cents / 100 },
  ];
  kpiCells.forEach(({ ref, value }) => {
    const cell = sheet.getCell(ref);
    cell.value = value;
    cell.numFmt = CURRENCY_FORMAT;
    cell.font = { bold: true };
    cell.alignment = { horizontal: "right" };
  });

  const headerRowNumber = 8;
  const headerRow = sheet.getRow(headerRowNumber);
  headerRow.values = [
    t("finance.fields.date"),
    t("finance.fields.description"),
    t("finance.fields.type"),
    t("finance.fields.label"),
    t("finance.fields.amount"),
  ];
  headerRow.eachCell((cell) => {
    cell.font = { bold: true };
    cell.fill = { type: "pattern", pattern: "solid", fgColor: { argb: TABLE_HEADER_BG } };
    cell.border = { bottom: { style: "thin" } };
  });

  movements.value.forEach((movement, index) => {
    const row = sheet.getRow(headerRowNumber + 1 + index);
    const amount = displayCents(movement) / 100;
    row.values = [movement.date, movement.description, typeLine(movement), movementLabelName(movement), amount];
    const amountCell = row.getCell(5);
    amountCell.numFmt = CURRENCY_FORMAT;
    amountCell.font = { color: { argb: amount < 0 ? NEGATIVE_TEXT : POSITIVE_TEXT } };
  });

  // Auto-fit por contenido: se salta las filas 1-2 (banner fusionado A:E, cuyo texto
  // completo vive en la columna A y no debe dictar su ancho) y mide el resto.
  sheet.columns.forEach((column, columnIndex) => {
    let maxLength = AUTO_FIT_MIN_WIDTH;
    for (let rowNumber = AUTO_FIT_START_ROW; rowNumber <= sheet.rowCount; rowNumber++) {
      const cellValue = sheet.getRow(rowNumber).getCell(columnIndex + 1).value;
      const length = cellValue != null ? String(cellValue).length : 0;
      if (length > maxLength) maxLength = length;
    }
    column.width = maxLength + 2;
  });

  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `ElosuE_Informe_${dateFrom.value}_${dateTo.value}.xlsx`;
  link.click();
  URL.revokeObjectURL(url);
}

function exportPdf() {
  const win = window.open("", "_blank");
  if (!win) return;

  const rows = movements.value
    .map(
      (movement) => `
        <tr>
          <td>${escapeHtml(movement.date)}</td>
          <td>${escapeHtml(movement.description)}</td>
          <td>${escapeHtml(typeLine(movement))}</td>
          <td>${escapeHtml(movementLabelName(movement))}</td>
          <td style="text-align:right">${escapeHtml(formatCurrency(displayCents(movement)))}</td>
        </tr>`,
    )
    .join("");

  win.document.write(`
    <!doctype html>
    <html lang="es">
      <head>
        <meta charset="utf-8" />
        <title>${escapeHtml(t("finance.reports.title"))}</title>
        <style>
          body { font-family: sans-serif; color: #1e293b; padding: 24px; }
          h1 { font-size: 20px; }
          .range { color: #64748b; margin-bottom: 16px; }
          .totals { display: flex; gap: 24px; margin-bottom: 16px; }
          .totals div { font-size: 14px; }
          table { width: 100%; border-collapse: collapse; font-size: 13px; }
          th, td { border-bottom: 1px solid #e2e8f0; padding: 8px; text-align: left; }
          th { text-transform: uppercase; font-size: 11px; color: #64748b; }
        </style>
      </head>
      <body>
        <h1>${escapeHtml(t("finance.reports.title"))}</h1>
        <p class="range">${escapeHtml(dateFrom.value)} — ${escapeHtml(dateTo.value)}</p>
        <div class="totals">
          <div><strong>${escapeHtml(t("finance.reports.summary.income"))}:</strong> ${escapeHtml(formatCurrency(totals.value.income_cents))}</div>
          <div><strong>${escapeHtml(t("finance.reports.summary.expense"))}:</strong> ${escapeHtml(formatCurrency(-totals.value.expense_cents))}</div>
          <div><strong>${escapeHtml(t("finance.reports.summary.net"))}:</strong> ${escapeHtml(formatCurrency(totals.value.net_cents))}</div>
        </div>
        <table>
          <thead>
            <tr>
              <th>${escapeHtml(t("finance.fields.date"))}</th>
              <th>${escapeHtml(t("finance.fields.description"))}</th>
              <th>${escapeHtml(t("finance.fields.type"))}</th>
              <th>${escapeHtml(t("finance.fields.label"))}</th>
              <th>${escapeHtml(t("finance.fields.amount"))}</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </body>
    </html>
  `);
  win.document.close();
  win.focus();
  win.print();
}

onMounted(() => {
  loadLabels();
  loadReport();
});
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-slate-800">{{ t("finance.reports.title") }}</h1>

    <Card class="mt-6 p-4">
      <div class="flex flex-wrap items-end gap-4">
        <FormField :label="t('finance.reports.filters.dateFrom')" input-id="report-date-from">
          <FormInput id="report-date-from" v-model="dateFrom" type="date" />
        </FormField>
        <FormField :label="t('finance.reports.filters.dateTo')" input-id="report-date-to">
          <FormInput id="report-date-to" v-model="dateTo" type="date" />
        </FormField>
        <Button variant="secondary" type="button" @click="setLastMonth">
          {{ t("finance.reports.filters.lastMonth") }}
        </Button>
        <Button variant="secondary" type="button" @click="setCurrentMonth">
          {{ t("finance.reports.filters.currentMonth") }}
        </Button>
        <FormField :label="t('finance.reports.filters.type')" input-id="report-scope">
          <FormSelect id="report-scope" v-model="scope">
            <option value="">{{ t("finance.reports.filters.allTypes") }}</option>
            <option value="cash">{{ t("finance.methods.cash") }}</option>
            <option value="card">{{ t("finance.methods.card") }}</option>
          </FormSelect>
        </FormField>
        <FormField :label="t('finance.reports.filters.label')" input-id="report-label">
          <FormSelect id="report-label" v-model="labelId">
            <option value="">{{ t("finance.reports.filters.allLabels") }}</option>
            <option v-for="label in labels" :key="label.id" :value="label.id">{{ label.name }}</option>
          </FormSelect>
        </FormField>
      </div>
    </Card>

    <p v-if="errorMessage" class="mt-2 text-sm text-red-600">{{ errorMessage }}</p>

    <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
      <Card class="p-4">
        <p class="text-sm text-slate-500">{{ t("finance.reports.summary.income") }}</p>
        <p class="mt-1 text-2xl font-semibold text-emerald-600">
          {{ loading ? "…" : formatCurrency(totals.income_cents) }}
        </p>
      </Card>
      <Card class="p-4">
        <p class="text-sm text-slate-500">{{ t("finance.reports.summary.expense") }}</p>
        <p class="mt-1 text-2xl font-semibold text-red-600">
          {{ loading ? "…" : formatCurrency(-totals.expense_cents) }}
        </p>
      </Card>
      <Card class="p-4">
        <p class="text-sm text-slate-500">{{ t("finance.reports.summary.net") }}</p>
        <p class="mt-1 text-2xl font-semibold" :class="totals.net_cents < 0 ? 'text-red-600' : 'text-slate-800'">
          {{ loading ? "…" : formatCurrency(totals.net_cents) }}
        </p>
      </Card>
    </div>

    <div class="mt-6 flex items-center justify-end gap-2">
      <button
        type="button"
        :disabled="movements.length === 0"
        class="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 shadow-sm transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        @click="exportExcel"
      >
        <Icon name="lucide:file-spreadsheet" class="text-emerald-600" />
        {{ t("finance.reports.export.excel") }}
      </button>
      <button
        type="button"
        :disabled="movements.length === 0"
        class="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 shadow-sm transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        @click="exportPdf"
      >
        <Icon name="lucide:file-text" class="text-red-600" />
        {{ t("finance.reports.export.pdf") }}
      </button>
    </div>

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
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="5" class="px-4 py-6 text-center text-slate-500">{{ t("finance.loading") }}</td>
            </tr>
            <tr v-else-if="movements.length === 0">
              <td colspan="5" class="px-4 py-6 text-center text-slate-500">{{ t("finance.reports.empty") }}</td>
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
                <span :class="displayCents(movement) < 0 ? 'text-red-600' : 'text-emerald-600'">
                  {{ formatCurrency(displayCents(movement)) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  </div>
</template>
