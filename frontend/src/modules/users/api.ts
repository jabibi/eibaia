import { apiFetch } from "~/core/api/http";

export type UserStatus = "active" | "inactive" | "new" | "all";

export interface UserItem {
  uid: string;
  email: string | null;
  display_name: string | null;
  photo_url: string | null;
  role_id: string | null;
  disabled: boolean;
}

interface UserListResponse {
  users: UserItem[];
  next_page_token: string | null;
}

export function listUsers(status: UserStatus = "active") {
  return apiFetch<UserListResponse>("/users", { query: { status } });
}

export interface UsersSummary {
  active: number;
  new: number;
  inactive: number;
}

export async function getUsersSummary(): Promise<UsersSummary> {
  const { users } = await listUsers("all");
  return {
    active: users.filter((u) => !u.disabled).length,
    new: users.filter((u) => !u.disabled && u.role_id === null).length,
    inactive: users.filter((u) => u.disabled).length,
  };
}

export function updateUserRole(uid: string, roleId: string) {
  return apiFetch<UserItem>(`/users/${uid}/role`, {
    method: "PATCH",
    body: { role_id: roleId },
  });
}

export function updateUserActive(uid: string, active: boolean) {
  return apiFetch<UserItem>(`/users/${uid}/active`, {
    method: "PATCH",
    body: { active },
  });
}
