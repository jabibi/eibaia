import { apiFetch } from "~/core/api/http";

export type MovementType = "expense" | "income" | "adjustment";
export type PaymentMethod = "cash" | "card";
export type MovementStatus = "draft" | "confirmed";
export type MovementScope = "cash" | "card";

export interface Movement {
  id: string;
  type: MovementType;
  method: PaymentMethod | null;
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

export function getSummary() {
  return apiFetch<FinanceSummary>("/finance/summary");
}

export function listMovements(pageToken?: string | null, status?: MovementStatus, scope?: MovementScope) {
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
