#!/usr/bin/env python3
"""Replicate Card & Krueger (1994) Table 2: pre-treatment employment.

FTE = EMPFT + NMGRS + 0.5 * EMPPT

If any of the three components is missing, FTE stays missing (do not
fill with zero).  Group by STATE and report the valid sample size,
mean FTE, and the standard error of the mean.

STATE = 1  -> New Jersey
STATE = 0  -> Pennsylvania

Uses only the Python standard library (no pandas required).
"""

import csv
import math

DATA_PATH = "data/public.csv"

STATE_LABELS = {1: "New Jersey", 0: "Pennsylvania"}


def parse_float(value: str):
    """Return a float for a non-empty numeric string, else None (missing)."""
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def main() -> None:
    fte_by_state = {0: [], 1: []}
    total_rows = 0
    missing_any = 0

    with open(DATA_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1

            empft = parse_float(row["EMPFT"])
            emppt = parse_float(row["EMPPT"])
            nmgrs = parse_float(row["NMGRS"])

            if empft is None or emppt is None or nmgrs is None:
                missing_any += 1
                continue

            fte = empft + nmgrs + 0.5 * emppt

            state = parse_float(row["STATE"])
            if state is None:
                continue
            state = int(state)
            if state in fte_by_state:
                fte_by_state[state].append(fte)

    print("=== Card & Krueger (1994) Table 2: pre-treatment employment ===\n")
    print("FTE = EMPFT + NMGRS + 0.5 * EMPPT\n")

    for state in (0, 1):
        values = fte_by_state[state]
        n = len(values)
        if n == 0:
            mean = sem = float("nan")
        else:
            mean = sum(values) / n
            variance = sum((x - mean) ** 2 for x in values) / (n - 1)
            sem = math.sqrt(variance / n)

        label = STATE_LABELS.get(state, f"STATE={state}")
        print(f"STATE={state} ({label})")
        print(f"  Valid sample size (N): {n}")
        print(f"  Mean FTE             : {mean:.4f}")
        print(f"  Standard error (SEM) : {sem:.4f}\n")

    print(f"Total rows: {total_rows}")
    print(
        "Rows with any of EMPFT/EMPPT/NMGRS missing: "
        f"{missing_any}"
    )


if __name__ == "__main__":
    main()
