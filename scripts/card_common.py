#!/usr/bin/env python3
"""Shared helpers for the Card & Krueger (1994) replication.

Centralizes data loading, FTE construction, and operating-status handling
so that every script applies the same rules (single source of truth).

FTE definitions:

    before = EMPFT + NMGRS + 0.5 * EMPPT
    after  = EMPFT2 + NMGRS2 + 0.5 * EMPPT2

Operating-status rules for the after wave (STATUS2):

    3           permanent closure  -> after FTE = 0
    2, 4, 5     temporary closure  -> after FTE missing (or 0 in the
                                      "temporary closures set to 0" variant)
    otherwise   after FTE from components (missing if any component missing)
"""

import csv
import math
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "public.csv")

STATE_LABELS = {1: "New Jersey", 0: "Pennsylvania"}
TEMPORARY_CLOSURE = {"2", "4", "5"}


def parse_float(value):
    """Return a float for a non-empty numeric string, else None (missing)."""
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def compute_fte_before(row):
    """Return pre-treatment FTE, or None if any component is missing."""
    empft = parse_float(row["EMPFT"])
    emppt = parse_float(row["EMPPT"])
    nmgrs = parse_float(row["NMGRS"])
    if empft is None or emppt is None or nmgrs is None:
        return None
    return empft + nmgrs + 0.5 * emppt


def compute_fte_after(row, temp_closed_to_zero=False):
    """Return post-treatment FTE per the STATUS2 rules, or None if missing.

    If ``temp_closed_to_zero`` is True, temporarily closed stores
    (STATUS2 in {2, 4, 5}) get after FTE = 0 instead of missing.
    """
    status2 = row["STATUS2"].strip()
    if status2 == "3":
        return 0.0  # permanent closure
    if status2 in TEMPORARY_CLOSURE:
        return 0.0 if temp_closed_to_zero else None
    empft2 = parse_float(row["EMPFT2"])
    emppt2 = parse_float(row["EMPPT2"])
    nmgrs2 = parse_float(row["NMGRS2"])
    if empft2 is None or emppt2 is None or nmgrs2 is None:
        return None
    return empft2 + nmgrs2 + 0.5 * emppt2


def load_records():
    """Return a list of dicts with the fields needed by every script.

    Keys: state, wage_st, status2, fte_before, fte_after, fte_after_temp0.

    Only STATE values 0 (Pennsylvania) and 1 (New Jersey) are kept.
    """
    records = []
    with open(DATA_PATH, newline="") as f:
        for row in csv.DictReader(f):
            state = parse_float(row["STATE"])
            if state is None:
                continue
            state = int(state)
            if state not in STATE_LABELS:
                continue

            status2_raw = row["STATUS2"].strip()
            status2 = int(status2_raw) if status2_raw != "" else None

            records.append(
                {
                    "state": state,
                    "wage_st": parse_float(row["WAGE_ST"]),
                    "status2": status2,
                    "fte_before": compute_fte_before(row),
                    "fte_after": compute_fte_after(row),
                    "fte_after_temp0": compute_fte_after(
                        row, temp_closed_to_zero=True
                    ),
                }
            )
    return records


def summarize(values):
    """Return (n, mean, sem); sem is None when n < 2."""
    n = len(values)
    if n == 0:
        return 0, None, None
    mean = sum(values) / n
    if n < 2:
        return n, mean, None
    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    sem = math.sqrt(variance / n)
    return n, mean, sem
