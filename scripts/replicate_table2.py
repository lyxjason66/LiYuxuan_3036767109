#!/usr/bin/env python3
"""Replicate Card & Krueger (1994) Table 2: FTE employment by state and wave.

Data loading, FTE construction, and operating-status rules are shared with
the other scripts via card_common (single source of truth).

FTE (before) = EMPFT + NMGRS + 0.5 * EMPPT
FTE (after)  = EMPFT2 + NMGRS2 + 0.5 * EMPPT2

Each wave uses only its own valid records; no balanced two-wave panel is
imposed.  The standard error of the mean is the sample standard deviation
divided by sqrt(n), and is reported as missing when n < 2.

STATE = 1 -> New Jersey
STATE = 0 -> Pennsylvania

Results are written to outputs/table2_fte_summary.csv (path is derived
from this script's location, not the current working directory) and are
also printed to the terminal.
"""

import csv
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import card_common

OUTPUT_DIR = os.path.join(card_common.PROJECT_ROOT, "outputs")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "table2_fte_summary.csv")

PERIODS = ("before", "after")
FIELD_NAMES = ["state", "state_name", "period", "n", "mean_fte", "se_mean"]


def main():
    records = card_common.load_records()

    fte = {"before": {0: [], 1: []}, "after": {0: [], 1: []}}
    for rec in records:
        if rec["fte_before"] is not None:
            fte["before"][rec["state"]].append(rec["fte_before"])
        if rec["fte_after"] is not None:
            fte["after"][rec["state"]].append(rec["fte_after"])

    rows = []
    for period in PERIODS:
        for state in (0, 1):
            n, mean, sem = card_common.summarize(fte[period][state])
            rows.append(
                {
                    "state": state,
                    "state_name": card_common.STATE_LABELS[state],
                    "period": period,
                    "n": n,
                    "mean_fte": mean,
                    "se_mean": sem,
                }
            )

    # Write CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELD_NAMES)
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "state": r["state"],
                    "state_name": r["state_name"],
                    "period": r["period"],
                    "n": r["n"],
                    "mean_fte": "" if r["mean_fte"] is None else f"{r['mean_fte']:.6f}",
                    "se_mean": "" if r["se_mean"] is None else f"{r['se_mean']:.6f}",
                }
            )

    # Print to terminal
    print("=== Card & Krueger (1994) Table 2: FTE by state and wave ===\n")
    print(f"{'State':<12} {'Period':<8} {'N':>4}  {'Mean FTE':>10}  {'SE':>10}")
    print("-" * 52)
    for r in rows:
        mean_s = "NA" if r["mean_fte"] is None else f"{r['mean_fte']:.6f}"
        sem_s = "NA" if r["se_mean"] is None else f"{r['se_mean']:.6f}"
        print(
            f"{r['state_name']:<12} {r['period']:<8} "
            f"{r['n']:>4}  {mean_s:>10}  {sem_s:>10}"
        )
    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
