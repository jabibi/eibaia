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
