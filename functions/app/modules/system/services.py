from firebase_admin import auth as firebase_auth

from app.core.firebase import get_db
from app.modules.finance.services import seed_defaults as seed_finance_defaults
from app.modules.roles.services import seed_defaults as seed_roles_defaults

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


def _delete_all_collections() -> None:
    """Wipes every top-level Firestore collection, whatever it's called — this
    introspects the live database instead of relying on a hardcoded/registered
    list, so it can never drift out of sync when a collection is renamed or a
    new one is added (as happened before: this list once said
    "finance_movements" long after that collection had been renamed, and never
    even mentioned "cashbox")."""
    db = get_db()
    for collection_ref in db.collections():
        _delete_all_documents(collection_ref.id)


def seed_defaults() -> None:
    """Basic data the app needs to be usable right after a factory reset (or
    on a brand new project with an empty database). Add a new module's own
    seed_defaults() call here as new bootstrap data is needed — this is the
    single place that wires a module into the post-reset setup."""
    seed_roles_defaults()  # required first: nobody could be granted any permission without it
    seed_finance_defaults()


def factory_reset() -> None:
    _delete_all_collections()
    _delete_all_users()
    seed_defaults()
