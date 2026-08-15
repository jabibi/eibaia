"""Inicialización del Firebase Admin SDK (singleton compartido por toda la app)."""

from pathlib import Path

import firebase_admin
from firebase_admin import auth, credentials, firestore

_LOCAL_SERVICE_ACCOUNT = Path(__file__).resolve().parents[2] / "serviceAccountKey.json"

if not firebase_admin._apps:
    if _LOCAL_SERVICE_ACCOUNT.exists():
        # Desarrollo local: credenciales explícitas de la cuenta de servicio.
        firebase_admin.initialize_app(credentials.Certificate(str(_LOCAL_SERVICE_ACCOUNT)))
    else:
        # Cloud Functions: credenciales por defecto del entorno gestionado.
        firebase_admin.initialize_app()


def get_db():
    return firestore.client()


def get_auth():
    return auth
