"""One-off script: seeds a default `cashbox` document so cash movements have
somewhere to attach to. NOT a Cloud Function — run manually, once, against a
target project (or again later to add another physical safe).

Usage (from functions/):
    venv/bin/python scripts/seed_cashbox.py ["Nombre de la caja"]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # functions/ on sys.path

from app.core.firebase import get_db  # noqa: E402  (also initializes the Admin SDK)
from app.modules.finance import services  # noqa: E402
from app.modules.finance.schemas import CashboxIn  # noqa: E402

DEFAULT_NAME = "La caja"


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_NAME
    db = get_db()

    existing = list(db.collection(services.CASHBOX_COLLECTION).where("name", "==", name).limit(1).stream())
    if existing:
        print(f"cashbox {name!r} already exists ({existing[0].id}), skipping")
        return

    cashbox = services.create_cashbox(CashboxIn(name=name))
    print(f"cashbox/{cashbox.id} seeded: {cashbox.name!r}")


if __name__ == "__main__":
    main()
