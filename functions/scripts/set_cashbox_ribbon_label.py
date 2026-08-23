"""One-off script: sets (or clears) the `ribbon_label` field on the single cashbox
doc. This is a per-environment marker, not app data — it's what makes the corner
ribbon appear (see core/components/RibbonBanner.vue on the frontend) so you can
tell at a glance which Firestore project a running app is actually talking to.
Leave it null in the real production project; set it (e.g. "TEST") in whichever
project is currently playing the role of "local/dev".

Usage (from functions/):
    venv/bin/python scripts/set_cashbox_ribbon_label.py TEST
    venv/bin/python scripts/set_cashbox_ribbon_label.py ""   # clears it (sets null)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # functions/ on sys.path

from app.modules.finance import services  # noqa: E402  (also initializes the Admin SDK)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    label = sys.argv[1] or None
    cashboxes = services.list_cashboxes()
    if not cashboxes:
        print("no cashbox found — run seed_cashbox.py first")
        sys.exit(1)
    if len(cashboxes) > 1:
        print(f"warning: {len(cashboxes)} cashboxes found, only marking the first ({cashboxes[0].id})")

    updated = services.set_cashbox_ribbon_label(cashboxes[0].id, label)
    print(f"cashbox/{updated.id} ribbon_label = {updated.ribbon_label!r}")


if __name__ == "__main__":
    main()
