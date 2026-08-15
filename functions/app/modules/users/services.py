from firebase_admin import auth as firebase_auth

from .schemas import Role, UserOut


def _to_user_out(user_record: firebase_auth.UserRecord) -> UserOut:
    claims = user_record.custom_claims or {}
    return UserOut(
        uid=user_record.uid,
        email=user_record.email,
        display_name=user_record.display_name,
        photo_url=user_record.photo_url,
        role=claims.get("role", "user"),
        disabled=user_record.disabled,
    )


def list_users(page_token: str | None = None, max_results: int = 100):
    page = firebase_auth.list_users(page_token=page_token, max_results=max_results)
    return [_to_user_out(u) for u in page.users], page.next_page_token or None


def set_user_role(uid: str, role: Role) -> UserOut:
    user_record = firebase_auth.get_user(uid)
    claims = dict(user_record.custom_claims or {})
    claims["role"] = role
    firebase_auth.set_custom_user_claims(uid, claims)
    return _to_user_out(firebase_auth.get_user(uid))
