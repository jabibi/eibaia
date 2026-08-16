import { apiFetch } from "~/core/api/http";

export interface UserRole {
  id: string;
  name: string;
  description: string;
  group_ids: string[];
}

export function listRoles() {
  return apiFetch<UserRole[]>("/roles");
}
