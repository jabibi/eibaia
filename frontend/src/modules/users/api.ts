import { apiFetch } from "~/core/api/http";

export type Role = "admin" | "manager" | "user";
export type UserStatus = "active" | "inactive" | "new";

export interface UserItem {
  uid: string;
  email: string | null;
  display_name: string | null;
  photo_url: string | null;
  role: Role | null;
  disabled: boolean;
}

interface UserListResponse {
  users: UserItem[];
  next_page_token: string | null;
}

export function listUsers(status: UserStatus = "active") {
  return apiFetch<UserListResponse>("/users", { query: { status } });
}

export function updateUserRole(uid: string, role: Role) {
  return apiFetch<UserItem>(`/users/${uid}/role`, {
    method: "PATCH",
    body: { role },
  });
}

export function updateUserActive(uid: string, active: boolean) {
  return apiFetch<UserItem>(`/users/${uid}/active`, {
    method: "PATCH",
    body: { active },
  });
}
