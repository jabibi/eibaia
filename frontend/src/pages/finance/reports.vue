<script setup lang="ts">
import { Workbook } from "exceljs";
import {
  getReport,
  listCategories,
  type Category,
  type Movement,
  type PaymentMethod,
  type ReportTotals,
} from "~/modules/finance/api";
import { formatCurrency } from "~/core/utils/currency";
import { formatShortDate } from "~/core/utils/date";
import { currentMonthRange, previousMonthRange } from "~/core/utils/dateRange";
import { usePermissionsStore } from "~/core/stores/permissions";
import Button from "~/core/components/ui/Button.vue";
import Card from "~/core/components/ui/Card.vue";
import FormField from "~/core/components/ui/FormField.vue";
import FormInput from "~/core/components/ui/FormInput.vue";
import FormSelect from "~/core/components/ui/FormSelect.vue";
import { tableCellAmountClass, tableCellClass, tableHeaderCellClass, tableRowClass } from "~/core/ui/tableClasses";
import { CATEGORY_COLOR_CLASSES } from "~/core/ui/categoryColors";

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
const categoryId = ref("");

const categories = ref<Category[]>([]);
const movements = ref<Movement[]>([]);
const totals = ref<ReportTotals>({ income_cents: 0, expense_cents: 0, net_cents: 0 });
const loading = ref(true);
const errorMessage = ref("");

const categoryById = computed(() => new Map(categories.value.map((category) => [category.id, category])));

function categoryFor(movement: Movement): Category | null {
  if (!movement.category_id) return null;
  return categoryById.value.get(movement.category_id) ?? null;
}

function movementCategoryName(movement: Movement): string {
  return categoryFor(movement)?.name ?? "—";
}

function typeLine(movement: Movement): string {
  const parts = [t(`finance.types.${movement.type}`)];
  if (movement.method) parts.push(t(`finance.methods.${movement.method}`));
  return parts.join(" ");
}

function displayCents(movement: Movement): number {
  return movement.type === "expense" ? -movement.amount_cents : movement.amount_cents;
}

function typeColorClass(movement: Movement): string {
  return movement.type === "expense" ? "text-red-600" : "text-emerald-600";
}

function typeIcon(movement: Movement): string {
  return movement.type === "expense" ? "lucide:arrow-down" : "lucide:arrow-up";
}

function methodIcon(movement: Movement): string | null {
  if (!movement.method) return null;
  return movement.method === "card" ? "lucide:credit-card" : "lucide:coins";
}

const scopeLabel = computed(() =>
  scope.value ? t(`finance.methods.${scope.value}`) : t("finance.reports.filters.allTypes"),
);

const categoryFilterLabel = computed(() => {
  if (!categoryId.value) return t("finance.reports.filters.allCategories");
  return categoryById.value.get(categoryId.value)?.name ?? t("finance.reports.filters.allCategories");
});

async function loadCategories() {
  const response = await listCategories();
  categories.value = response.categories;
}

async function loadReport() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const result = await getReport({
      date_from: dateFrom.value,
      date_to: dateTo.value,
      scope: scope.value || undefined,
      category_id: categoryId.value || undefined,
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
watch([dateFrom, dateTo, scope, categoryId], () => {
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
const REPORT_COLUMN_COUNT = 6; // Tipo, Fecha, Concepto, Categoría, Trabajadora, Importe

async function exportExcel() {
  const workbook = new Workbook();
  const sheet = workbook.addWorksheet(t("finance.reports.export.sheetName"));

  sheet.mergeCells("A1:F1");
  const titleCell = sheet.getCell("A1");
  titleCell.value = t("finance.reports.export.docTitle").toUpperCase();
  titleCell.font = { name: "Arial", size: 14, bold: true, color: { argb: HEADER_TEXT } };
  titleCell.alignment = { horizontal: "center", vertical: "middle" };
  titleCell.fill = { type: "pattern", pattern: "solid", fgColor: { argb: HEADER_BG } };

  sheet.mergeCells("A2:F2");
  const filtersCell = sheet.getCell("A2");
  filtersCell.value = [
    t("finance.reports.export.periodLabel", { from: dateFrom.value, to: dateTo.value }),
    `${t("finance.reports.filters.type")}: ${scopeLabel.value}`,
    `${t("finance.reports.filters.category")}: ${categoryFilterLabel.value}`,
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
    t("finance.fields.type"),
    t("finance.fields.date"),
    t("finance.fields.description"),
    t("finance.fields.category"),
    t("finance.fields.worker"),
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
    const amountColor = amount < 0 ? NEGATIVE_TEXT : POSITIVE_TEXT;
    row.values = [
      typeLine(movement),
      movement.date,
      movement.description,
      movementCategoryName(movement),
      movement.worker_name ?? "—",
      amount,
    ];
    row.getCell(1).font = { color: { argb: amountColor } };
    const amountCell = row.getCell(REPORT_COLUMN_COUNT);
    amountCell.numFmt = CURRENCY_FORMAT;
    amountCell.font = { color: { argb: amountColor } };
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
    .map((movement) => {
      const amountClass = movement.type === "expense" ? "negative" : "positive";
      return `
        <tr>
          <td class="${amountClass}">${escapeHtml(typeLine(movement))}</td>
          <td>${escapeHtml(movement.date)}</td>
          <td>${escapeHtml(movement.description)}</td>
          <td>${escapeHtml(movementCategoryName(movement))}</td>
          <td>${escapeHtml(movement.worker_name ?? "—")}</td>
          <td class="amount ${amountClass}">${escapeHtml(formatCurrency(displayCents(movement)))}</td>
        </tr>`;
    })
    .join("");

  win.document.write(`
    <!doctype html>
    <html lang="es">
      <head>
        <meta charset="utf-8" />
        <title>${escapeHtml(t("finance.reports.title"))}</title>
        <style>
          @page { margin: 1cm; size: auto; }
          @media print {
            * {
              -webkit-print-color-adjust: exact !important;
              print-color-adjust: exact !important;
            }
          }
          body { font-family: Arial, sans-serif; color: #1e293b; margin: 0; }
          .banner {
            background: #0f766e; color: #fff; text-align: center; padding: 16px 24px;
            font-size: 16px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.02em;
          }
          .filters {
            background: #f8fafc; color: #64748b; font-size: 11px; font-style: italic;
            text-align: center; padding: 8px 24px; border-bottom: 1px solid #e2e8f0;
          }
          .content { padding: 20px 24px; }
          .summary-title { font-weight: bold; font-size: 12px; text-transform: uppercase; margin-bottom: 8px; }
          .summary { display: flex; gap: 32px; margin-bottom: 20px; }
          .summary div { font-size: 13px; }
          .summary strong { font-weight: bold; }
          table { width: 100%; border-collapse: collapse; font-size: 12px; }
          th, td { border-bottom: 1px solid #e2e8f0; padding: 8px; text-align: left; }
          th {
            text-transform: uppercase; font-size: 10px; color: #64748b;
            background: #f1f5f9; font-weight: bold;
          }
          td.amount, th.amount { text-align: right; }
          .negative { color: #dc2626; }
          .positive { color: #059669; }
        </style>
      </head>
      <body>
        <div class="banner">${escapeHtml(t("finance.reports.export.docTitle"))}</div>
        <div class="filters">
          ${escapeHtml(t("finance.reports.export.periodLabel", { from: dateFrom.value, to: dateTo.value }))}
          |
          ${escapeHtml(t("finance.reports.filters.type"))}: ${escapeHtml(scopeLabel.value)}
          |
          ${escapeHtml(t("finance.reports.filters.category"))}: ${escapeHtml(categoryFilterLabel.value)}
        </div>
        <div class="content">
          <div class="summary-title">${escapeHtml(t("finance.reports.export.summaryTitle"))}</div>
          <div class="summary">
            <div><strong>${escapeHtml(t("finance.reports.summary.income"))}:</strong> ${escapeHtml(formatCurrency(totals.value.income_cents))}</div>
            <div><strong>${escapeHtml(t("finance.reports.summary.expense"))}:</strong> ${escapeHtml(formatCurrency(-totals.value.expense_cents))}</div>
            <div><strong>${escapeHtml(t("finance.reports.summary.net"))}:</strong> ${escapeHtml(formatCurrency(totals.value.net_cents))}</div>
          </div>
          <table>
            <thead>
              <tr>
                <th>${escapeHtml(t("finance.fields.type"))}</th>
                <th>${escapeHtml(t("finance.fields.date"))}</th>
                <th>${escapeHtml(t("finance.fields.description"))}</th>
                <th>${escapeHtml(t("finance.fields.category"))}</th>
                <th>${escapeHtml(t("finance.fields.worker"))}</th>
                <th class="amount">${escapeHtml(t("finance.fields.amount"))}</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </body>
    </html>
  `);
  win.document.close();
  win.focus();
  win.print();
}

onMounted(() => {
  loadCategories();
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
        <FormField :label="t('finance.reports.filters.category')" input-id="report-category">
          <FormSelect id="report-category" v-model="categoryId">
            <option value="">{{ t("finance.reports.filters.allCategories") }}</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
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
              <th :class="tableHeaderCellClass">{{ t("finance.fields.type") }}</th>
              <th :class="tableHeaderCellClass">{{ t("finance.fields.date") }}</th>
              <th :class="tableHeaderCellClass">{{ t("finance.fields.description") }}</th>
              <th :class="tableHeaderCellClass">{{ t("finance.fields.category") }}</th>
              <th :class="tableHeaderCellClass">{{ t("finance.fields.worker") }}</th>
              <th :class="[tableHeaderCellClass, 'text-right']">{{ t("finance.fields.amount") }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="px-4 py-6 text-center text-slate-500">{{ t("finance.loading") }}</td>
            </tr>
            <tr v-else-if="movements.length === 0">
              <td colspan="6" class="px-4 py-6 text-center text-slate-500">{{ t("finance.reports.empty") }}</td>
            </tr>
            <tr v-for="movement in movements" :key="movement.id" :class="tableRowClass">
              <td :class="tableCellClass">
                <span class="inline-flex items-center gap-1.5" :title="typeLine(movement)">
                  <Icon :name="typeIcon(movement)" :class="typeColorClass(movement)" />
                  <Icon v-if="methodIcon(movement)" :name="methodIcon(movement)!" class="text-slate-400" />
                  <span class="sr-only">{{ typeLine(movement) }}</span>
                </span>
              </td>
              <td :class="tableCellClass">{{ formatShortDate(movement.date) }}</td>
              <td :class="tableCellClass">{{ movement.description }}</td>
              <td :class="tableCellClass">
                <span
                  v-if="categoryFor(movement)"
                  class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                  :class="[
                    CATEGORY_COLOR_CLASSES[categoryFor(movement)!.color].chipBg,
                    CATEGORY_COLOR_CLASSES[categoryFor(movement)!.color].text,
                  ]"
                >
                  {{ categoryFor(movement)!.name }}
                </span>
                <span v-else class="text-slate-400">—</span>
              </td>
              <td :class="tableCellClass">{{ movement.worker_name ?? "—" }}</td>
              <td :class="tableCellAmountClass">
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
