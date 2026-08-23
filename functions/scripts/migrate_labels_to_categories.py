"""One-off script: migrates the "Etiqueta" -> "Categoría" rename in Firestore.
Copies every doc from the old `cashbox_movement_label` collection into the new
`cashbox_movement_category` collection (same id, same fields), then on every
`cashbox_movement` doc renames the `label_id` field to `category_id`. Finally
deletes the now-migrated `cashbox_movement_label` docs. Safe to re-run — each
step is idempotent (skips docs that already look migrated).

Usage (from functions/):
    venv/bin/python scripts/migrate_labels_to_categories.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # functions/ on sys.path

from firebase_admin import firestore  # noqa: E402

from app.core.firebase import get_db, snapshot_data  # noqa: E402  (also initializes the Admin SDK)

LABEL_COLLECTION = "cashbox_movement_label"
CATEGORY_COLLECTION = "cashbox_movement_category"
MOVEMENT_COLLECTION = "cashbox_movement"


def main() -> None:
    db = get_db()

    label_docs = list(db.collection(LABEL_COLLECTION).stream())
    copied = 0
    for doc in label_docs:
        target = db.collection(CATEGORY_COLLECTION).document(doc.id)
        if target.get().exists:
            continue
        target.set(snapshot_data(doc))
        copied += 1
    print(f"copied {copied}/{len(label_docs)} categories from {LABEL_COLLECTION!r} to {CATEGORY_COLLECTION!r}")

    movement_docs = list(db.collection(MOVEMENT_COLLECTION).stream())
    migrated = 0
    for doc in movement_docs:
        data = snapshot_data(doc)
        if "label_id" not in data:
            continue
        doc.reference.update({"category_id": data["label_id"], "label_id": firestore.DELETE_FIELD})
        migrated += 1
    print(f"migrated {migrated}/{len(movement_docs)} movement(s): label_id -> category_id")

    deleted = 0
    for doc in label_docs:
        db.collection(LABEL_COLLECTION).document(doc.id).delete()
        deleted += 1
    print(f"deleted {deleted} legacy doc(s) from {LABEL_COLLECTION!r}")


if __name__ == "__main__":
    main()
