#!/usr/bin/env python3
"""Replicate Card & Krueger (1994) Table 3: state-level employment changes.

No regression here; only the between-state comparison of employment
changes (difference-in-differences).

Two samples, kept clearly separate:

  1. "all_valid" (unbalanced): each period uses its own valid records.

         state change = mean(after) - mean(before)
         DiD          = change_NewJersey - change_Pennsylvania

  2. "balanced": only stores with both pre- and post-treatment FTE.

         per-store change = after - before
         then mean change and its standard error by state, and the
         between-state difference of the mean changes.

The DiD standard error is intentionally NOT computed and no statistical
significance is claimed.  Full (unrounded) values are written; the
rounded figure DiD ~= 2.753606 is used only as a validation check.

Data loading, FTE construction, and operating-status rules are shared via
card_common (single source of truth).

STATE = 1 -> New Jersey
STATE = 0 -> Pennsylvania

Results are written to outputs/table3_did_summary.csv and printed.
"""

import csv
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import card_common

OUTPUT_DIR = os.path.join(card_common.PROJECT_ROOT, "outputs")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "table3_did_summary.csv")

FIELD_NAMES = ["sample", "state", "state_name", "stat", "value"]


def format_value(value):
    """Return a full-precision string for a value, or '' for None."""
    if value is None:
        return ""
    if isinstance(value, float):
        return repr(value)
    return str(value)


def main():
    records = card_common.load_records()

    # --- 1. all_valid (unbalanced) ---
    before = {0: [], 1: []}
    after = {0: [], 1: []}
    for rec in records:
        if rec["fte_before"] is not None:
            before[rec["state"]].append(rec["fte_before"])
        if rec["fte_after"] is not None:
            after[rec["state"]].append(rec["fte_after"])

    changes = {}
    for state in (0, 1):
        _, mean_before, _ = card_common.summarize(before[state])
        _, mean_after, _ = card_common.summarize(after[state])
        changes[state] = mean_after - mean_before
    did = changes[1] - changes[0]

    # --- 2. balanced ---
    change_by_state = {0: [], 1: []}
    for rec in records:
        if rec["fte_before"] is not None and rec["fte_after"] is not None:
            change_by_state[rec["state"]].append(
                rec["fte_after"] - rec["fte_before"]
            )

    balanced = {}
    for state in (0, 1):
        n, mean_change, se_change = card_common.summarize(change_by_state[state])
        balanced[state] = (n, mean_change, se_change)

    diff_mean_change = None
    if balanced[0][1] is not None and balanced[1][1] is not None:
        diff_mean_change = balanced[1][1] - balanced[0][1]

    # --- Build output rows (long format) ---
    rows = []
    for state in (0, 1):
        rows.append(
            {
                "sample": "all_valid",
                "state": state,
                "state_name": card_common.STATE_LABELS[state],
                "stat": "change",
                "value": changes[state],
            }
        )
    rows.append(
        {
            "sample": "all_valid",
            "state": "",
            "state_name": "",
            "stat": "did",
            "value": did,
        }
    )
    for state in (0, 1):
        n, mean_change, se_change = balanced[state]
        rows.append(
            {
                "sample": "balanced",
                "state": state,
                "state_name": card_common.STATE_LABELS[state],
                "stat": "n",
                "value": n,
            }
        )
        rows.append(
            {
                "sample": "balanced",
                "state": state,
                "state_name": card_common.STATE_LABELS[state],
                "stat": "mean_change",
                "value": mean_change,
            }
        )
        rows.append(
            {
                "sample": "balanced",
                "state": state,
                "state_name": card_common.STATE_LABELS[state],
                "stat": "se_change",
                "value": se_change,
            }
        )
    rows.append(
        {
            "sample": "balanced",
            "state": "",
            "state_name": "",
            "stat": "diff_mean_change",
            "value": diff_mean_change,
        }
    )

    # --- Write CSV ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELD_NAMES)
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "sample": r["sample"],
                    "state": r["state"],
                    "state_name": r["state_name"],
                    "stat": r["stat"],
                    "value": format_value(r["value"]),
                }
            )

    # --- Print to terminal ---
    print("=== Card & Krueger (1994) Table 3: state-level employment changes ===\n")

    print("[1] all_valid (unbalanced) -- each period uses its own valid records")
    for state in (0, 1):
        label = card_common.STATE_LABELS[state]
        print(
            f"    {label:<12} change = mean(after) - mean(before) = "
            f"{format_value(changes[state])}"
        )
    print(f"    {'DiD':<12} = NJ change - PA change = {format_value(did)}")
    print("    (rounded DiD ~= 2.753606, validation check only)\n")

    print("[2] balanced -- only stores with both pre- and post-treatment FTE")
    print(f"    {'State':<12} {'N':>4}  {'Mean change':>14}  {'SE(change)':>12}")
    print("    " + "-" * 46)
    for state in (0, 1):
        n, mean_change, se_change = balanced[state]
        label = card_common.STATE_LABELS[state]
        print(
            f"    {label:<12} {n:>4}  {format_value(mean_change):>14}  "
            f"{format_value(se_change):>12}"
        )
    print(
        "    Difference (NJ - PA) mean change = "
        f"{format_value(diff_mean_change)}"
    )
    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
