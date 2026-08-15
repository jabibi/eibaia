import { apiFetch } from "~/core/api/http";

export type Role = "admin" | "manager" | "user";

export interface UserItem {
  uid: string;
  email: string | null;
  display_name: string | null;
  photo_url: string | null;
  role: Role;
  disabled: boolean;
}

interface UserListResponse {
  users: UserItem[];
  next_page_token: string | null;
}

export function listUsers() {
  return apiFetch<UserListResponse>("/users");
}

export function updateUserRole(uid: string, role: Role) {
  return apiFetch<UserItem>(`/users/${uid}/role`, {
    method: "PATCH",
    body: { role },
  });
}
