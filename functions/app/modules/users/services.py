from firebase_admin import auth as firebase_auth

from .schemas import Role, UserOut, UserStatus


def _to_user_out(user_record: firebase_auth.UserRecord) -> UserOut:
    claims = user_record.custom_claims or {}
    return UserOut(
        uid=user_record.uid,
        email=user_record.email,
        display_name=user_record.display_name,
        photo_url=user_record.photo_url,
        role=claims.get("role"),
        disabled=user_record.disabled,
    )


def list_users(page_token: str | None = None, max_results: int = 100, status: UserStatus = "active"):
    page = firebase_auth.list_users(page_token=page_token, max_results=max_results)
    users = [_to_user_out(u) for u in page.users]

    if status == "active":
        users = [u for u in users if not u.disabled]
    elif status == "inactive":
        users = [u for u in users if u.disabled]
    elif status == "new":
        users = [u for u in users if u.role is None and not u.disabled]

    return users, page.next_page_token or None


def set_user_role(uid: str, role: Role) -> UserOut:
    user_record = firebase_auth.get_user(uid)
    claims = dict(user_record.custom_claims or {})
    claims["role"] = role
    firebase_auth.set_custom_user_claims(uid, claims)
    return _to_user_out(firebase_auth.get_user(uid))


def set_user_active(uid: str, active: bool) -> UserOut:
    firebase_auth.update_user(uid, disabled=not active)
    return _to_user_out(firebase_auth.get_user(uid))


def ensure_first_admin(uid: str) -> Role | None:
    """If no admin exists yet, promotes uid to admin. Returns the new role, or None if not applicable."""
    users, _ = list_users(status="all")
    if any(u.role == "admin" for u in users):
        return None
    set_user_role(uid, "admin")
    return "admin"
