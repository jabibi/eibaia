"""One-off script: seeds the permission_groups / user_roles Firestore collections
(via roles.services.seed_defaults()) and migrates existing Firebase Auth users'
legacy `role` custom claim to `role_id`. NOT a Cloud Function — run manually,
once, against a target project.

Usage (from functions/):
    venv/bin/python scripts/seed_rbac.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # functions/ on sys.path

from firebase_admin import auth as firebase_auth  # noqa: E402

from app.core.firebase import get_db  # noqa: E402  (also initializes the Admin SDK)
from app.modules.roles.services import seed_defaults  # noqa: E402

ROLE_CLAIM_MAP = {"admin": "admin", "manager": "manager", "user": "employee"}


def migrate_user_claims() -> None:
    for user in firebase_auth.list_users().iterate_all():
        claims = dict(user.custom_claims or {})
        if "role" not in claims:
            continue  # already migrated, or never had a role assigned
        old_role = claims.pop("role")
        claims["role_id"] = ROLE_CLAIM_MAP.get(old_role)
        firebase_auth.set_custom_user_claims(user.uid, claims)
        print(f"  {user.email or user.uid}: role={old_role!r} -> role_id={claims['role_id']!r}")


def main() -> None:
    get_db()  # also initializes the Admin SDK
    print("Seeding permission_groups and user_roles...")
    seed_defaults()
    print("Migrating Firebase Auth user claims (role -> role_id)...")
    migrate_user_claims()
    print("Done.")


if __name__ == "__main__":
    main()
