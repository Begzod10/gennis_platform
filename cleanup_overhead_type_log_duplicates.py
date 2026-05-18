"""One-shot cleanup for OverheadTypeLog rows whose `branch_id` does not match
their parent `OverheadType.branch_id`.

These were created by an older version of the monthly Celery generator that
looped `OverheadType x Branches` instead of using each OverheadType's own
`branch_id`. The generator is now fixed; this script soft-deletes the
historical garbage.

Usage:
    python cleanup_overhead_type_log_duplicates.py                # dry-run
    python cleanup_overhead_type_log_duplicates.py --apply        # actually soft-delete
    python cleanup_overhead_type_log_duplicates.py --apply --force-paid
                                                                  # include rows with is_paid=True

Dry-run is the default and always safe.
"""

import argparse
import os
import sys
from collections import Counter

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gennis_platform.settings")
django.setup()

from django.db.models import F  # noqa: E402
from overhead.models import OverheadTypeLog  # noqa: E402


def find_mismatched_logs():
    """Return non-deleted logs whose branch_id mismatches their parent OverheadType.branch_id."""
    return list(
        OverheadTypeLog.objects.select_related("overhead_type")
        .filter(
            deleted=False,
            branch_id__isnull=False,
            overhead_type__branch_id__isnull=False,
        )
        .exclude(branch_id=F("overhead_type__branch_id"))
        .order_by("date", "id")
    )


def summarize(rows):
    by_month = Counter()
    by_branch = Counter()
    paid_rows = [r for r in rows if r.is_paid]

    for r in rows:
        by_month[r.date] += 1
        by_branch[r.branch_id] += 1

    print(f"Total mismatched logs: {len(rows)}")
    print(f"Paid (is_paid=True): {len(paid_rows)}")
    print()
    print("By log.date:")
    for d, count in sorted(by_month.items(), key=lambda kv: kv[0] or kv[0]):
        print(f"  {d}: {count}")
    print()
    print("By log.branch_id:")
    for b, count in sorted(by_branch.items(), key=lambda kv: kv[0]):
        print(f"  branch_id={b}: {count}")

    if paid_rows:
        print()
        print("Paid rows (log_id, ot_id, log.branch_id, overhead_id):")
        for r in paid_rows[:20]:
            print(f"  log_id={r.id} ot_id={r.overhead_type_id} log_branch={r.branch_id} overhead_id={r.overhead_id}")
        if len(paid_rows) > 20:
            print(f"  ... and {len(paid_rows) - 20} more")
    return paid_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Actually soft-delete (default: dry-run)")
    parser.add_argument(
        "--force-paid",
        action="store_true",
        help="Include rows where is_paid=True (default: skip them; safer)",
    )
    args = parser.parse_args()

    rows = find_mismatched_logs()
    if not rows:
        print("No mismatched logs found. Nothing to do.")
        return 0

    paid_rows = summarize(rows)

    if not args.apply:
        print()
        print("Dry-run only. Re-run with --apply to soft-delete the rows above.")
        return 0

    targets = rows
    if paid_rows and not args.force_paid:
        print()
        print(
            f"Refusing to soft-delete {len(paid_rows)} paid rows without --force-paid. "
            "Skipping paid rows; unpaid rows will still be processed."
        )
        targets = [r for r in rows if not r.is_paid]

    target_ids = [r.id for r in targets]
    OverheadTypeLog.objects.filter(id__in=target_ids).update(deleted=True)
    print(f"Soft-deleted {len(target_ids)} logs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
