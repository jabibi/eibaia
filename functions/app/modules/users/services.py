from firebase_admin import auth as firebase_auth

from app.core.firebase import get_db, snapshot_data

from .schemas import DashboardPreferencesIn, DashboardPreferencesOut, UserOut, UserStatus

DASHBOARD_PREFS_COLLECTION = "dashboard_preferences"


def _to_user_out(user_record: firebase_auth.UserRecord) -> UserOut:
    claims = user_record.custom_claims or {}
    return UserOut(
        uid=user_record.uid,
        email=user_record.email,
        display_name=user_record.display_name,
        photo_url=user_record.photo_url,
        role_id=claims.get("role_id"),
        disabled=user_record.disabled,
    )


def list_users(page_token: str | None = None, max_results: int = 100, status: UserStatus = "active"):
    page = firebase_auth.list_users(page_token=page_token, max_results=max_results)
    users = [_to_user_out(u) for u in page.users]

    if status == "active":
        users = [u for u in users if not u.disabled and u.role_id is not None]
    elif status == "inactive":
        users = [u for u in users if u.disabled]
    elif status == "new":
        users = [u for u in users if u.role_id is None and not u.disabled]

    return users, page.next_page_token or None


def set_user_role(uid: str, role_id: str | None) -> UserOut:
    if role_id is not None and not get_db().collection("user_roles").document(role_id).get().exists:
        raise ValueError(f"Unknown role_id: {role_id}")

    user_record = firebase_auth.get_user(uid)
    claims = dict(user_record.custom_claims or {})
    if role_id is None:
        claims.pop("role_id", None)
    else:
        claims["role_id"] = role_id
    firebase_auth.set_custom_user_claims(uid, claims)
    return _to_user_out(firebase_auth.get_user(uid))


def set_user_active(uid: str, active: bool) -> UserOut:
    firebase_auth.update_user(uid, disabled=not active)
    return _to_user_out(firebase_auth.get_user(uid))


def ensure_first_admin(uid: str) -> str | None:
    """If no admin exists yet, promotes uid to the seeded 'admin' role. Returns
    the new role_id, or None if not applicable."""
    users, _ = list_users(status="all")
    if any(u.role_id == "admin" for u in users):
        return None
    set_user_role(uid, "admin")
    return "admin"


def get_permissions_for(role_id: str | None) -> list[str]:
    if role_id is None:
        return []
    doc = get_db().collection("user_roles").document(role_id).get()
    if not doc.exists:
        return []
    return list(snapshot_data(doc).get("group_ids", []))


def get_dashboard_preferences(uid: str) -> DashboardPreferencesOut:
    doc = get_db().collection(DASHBOARD_PREFS_COLLECTION).document(uid).get()
    if not doc.exists:
        return DashboardPreferencesOut(pinned_kpis=[])
    return DashboardPreferencesOut(pinned_kpis=snapshot_data(doc).get("pinned_kpis", []))


def set_dashboard_preferences(uid: str, payload: DashboardPreferencesIn) -> DashboardPreferencesOut:
    get_db().collection(DASHBOARD_PREFS_COLLECTION).document(uid).set(
        {"pinned_kpis": [kpi.model_dump() for kpi in payload.pinned_kpis]}
    )
    return DashboardPreferencesOut(pinned_kpis=payload.pinned_kpis)
