"""Firebase Admin SDK initialization (singleton shared across the app)."""

from pathlib import Path

import firebase_admin
from firebase_admin import auth, credentials, firestore

_LOCAL_SERVICE_ACCOUNT = Path(__file__).resolve().parents[2] / "serviceAccountKey.json"

if not firebase_admin._apps:
    if _LOCAL_SERVICE_ACCOUNT.exists():
        # Local development: explicit service account credentials.
        firebase_admin.initialize_app(credentials.Certificate(str(_LOCAL_SERVICE_ACCOUNT)))
    else:
        # Cloud Functions: default credentials from the managed environment.
        firebase_admin.initialize_app()


def get_db():
    return firestore.client()


def get_auth():
    return auth


def snapshot_data(doc) -> dict:
    """`doc.to_dict()` narrowed to a non-None dict.

    The Firestore client types `to_dict()` as `dict | None` because it returns
    None for a snapshot of a document that doesn't exist. Only call this once
    the caller has already established the document exists (via `.exists`, a
    query/stream result, or a write it just made) — otherwise this raises.
    """
    data = doc.to_dict()
    if data is None:
        raise ValueError(f"document {doc.reference.path} does not exist")
    return data
