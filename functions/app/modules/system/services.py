from firebase_admin import auth as firebase_auth

from app.core.firebase import get_db

_RESET_COLLECTIONS = ["finance_movements"]
_MAX_BATCH_DELETE = 1000


def _delete_all_documents(collection_name: str, batch_size: int = 200) -> None:
    db = get_db()
    while True:
        docs = list(db.collection(collection_name).limit(batch_size).stream())
        if not docs:
            break
        for doc in docs:
            doc.reference.delete()


def _delete_all_users() -> None:
    uids = [user.uid for user in firebase_auth.list_users().iterate_all()]
    for i in range(0, len(uids), _MAX_BATCH_DELETE):
        firebase_auth.delete_users(uids[i : i + _MAX_BATCH_DELETE])


def factory_reset() -> None:
    for collection_name in _RESET_COLLECTIONS:
        _delete_all_documents(collection_name)
    _delete_all_users()
