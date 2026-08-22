import { apiFetch } from "~/core/api/http";
import type { LabelColor } from "~/core/ui/labelColors";

export type MovementType = "expense" | "income";
export type PaymentMethod = "cash" | "card";
export type MovementStatus = "draft" | "confirmed";

export interface Movement {
  id: string;
  type: MovementType;
  method: PaymentMethod | null;
  cashbox_id: string | null;
  label_id: string | null;
  amount_cents: number;
  description: string;
  date: string;
  status: MovementStatus;
  created_by: string;
  created_by_name: string | null;
  created_at: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
}

export interface MovementInput {
  type: MovementType;
  method?: PaymentMethod | null;
  cashbox_id?: string | null;
  label_id?: string | null;
  amount_cents: number;
  description: string;
  date: string;
}

export type MovementUpdateInput = Partial<MovementInput>;

interface MovementListResponse {
  movements: Movement[];
  next_page_token: string | null;
}

export interface MonthlyStat {
  total_cents: number;
  count: number;
}

export interface FinanceSummary {
  balance_cents: number;
  cash_expenses_month: MonthlyStat;
  card_expenses_month: MonthlyStat;
  pending_drafts_count: number;
}

export interface Cashbox {
  id: string;
  name: string;
  total_amount_cents: number;
  last_update: string | null;
}

interface CashboxListResponse {
  cashboxes: Cashbox[];
}

export function getSummary() {
  return apiFetch<FinanceSummary>("/finance/summary");
}

export interface ReportTotals {
  income_cents: number;
  expense_cents: number;
  net_cents: number;
}

export interface ReportResult {
  movements: Movement[];
  totals: ReportTotals;
}

export function getReport(params: {
  date_from: string;
  date_to: string;
  scope?: PaymentMethod;
  label_id?: string;
}) {
  return apiFetch<ReportResult>("/finance/reports", { query: params });
}

export function listCashboxes() {
  return apiFetch<CashboxListResponse>("/finance/cashboxes");
}

export function createCashbox(payload: { name: string }) {
  return apiFetch<Cashbox>("/finance/cashboxes", { method: "POST", body: payload });
}

export interface Label {
  id: string;
  name: string;
  color: LabelColor;
}

interface LabelListResponse {
  labels: Label[];
}

export function listLabels() {
  return apiFetch<LabelListResponse>("/finance/labels");
}

export function createLabel(payload: { name: string; color: LabelColor }) {
  return apiFetch<Label>("/finance/labels", { method: "POST", body: payload });
}

export function updateLabel(id: string, payload: { name: string; color: LabelColor }) {
  return apiFetch<Label>(`/finance/labels/${id}`, { method: "PATCH", body: payload });
}

export function deleteLabel(id: string) {
  return apiFetch<void>(`/finance/labels/${id}`, { method: "DELETE" });
}

export function listMovements(pageToken?: string | null, status?: MovementStatus, scope?: PaymentMethod) {
  return apiFetch<MovementListResponse>("/finance/movements", {
    query: { page_token: pageToken ?? undefined, status, scope },
  });
}

export function getMovement(id: string) {
  return apiFetch<Movement>(`/finance/movements/${id}`);
}

export function createMovement(payload: MovementInput) {
  return apiFetch<Movement>("/finance/movements", { method: "POST", body: payload });
}

export function updateMovement(id: string, payload: MovementUpdateInput) {
  return apiFetch<Movement>(`/finance/movements/${id}`, { method: "PATCH", body: payload });
}

export function updateMovementStatus(id: string, status: MovementStatus) {
  return apiFetch<Movement>(`/finance/movements/${id}/status`, {
    method: "PATCH",
    body: { status },
  });
}

export function deleteMovement(id: string) {
  return apiFetch<void>(`/finance/movements/${id}`, { method: "DELETE" });
}
