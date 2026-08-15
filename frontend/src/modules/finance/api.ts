import { apiFetch } from "~/core/api/http";

export type MovementType = "expense" | "income" | "adjustment";
export type PaymentMethod = "cash" | "card";
export type MovementStatus = "draft" | "confirmed";

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

export function getBalance() {
  return apiFetch<{ balance_cents: number }>("/finance/balance");
}

export function getRecentMovements(limit = 10) {
  return apiFetch<Movement[]>("/finance/movements/recent", { query: { limit } });
}

export function listMovements(pageToken?: string | null, status?: MovementStatus) {
  return apiFetch<MovementListResponse>("/finance/movements", {
    query: { page_token: pageToken ?? undefined, status },
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
