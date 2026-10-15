#!/usr/bin/env python3
"""Export the restaurant-level (per-store) processed dataset.

Reads data/public.csv and writes one row per survey record to a local,
git-ignored file: data/processed/store_level.csv.

The dataset is a derived convenience for the assignment. It applies the SAME
rules as the replication scripts, never a separate copy:

    * FTE before / after / after-with-temporary-closures-zero -> card_common.
    * GAP -> replicate_table4.make_gap.
    * Table 4 primary / supplementary sample membership ->
      replicate_table4.qualifies_primary / qualifies_supplementary.
    * Table 3 balanced / temp0 and extension samples -> the same conditions
      the scripts use, expressed over card_common's fields.

SHEET is NOT treated as a unique key: duplicate SHEET values (if any) are kept
as-is, and every record is written.

The file is generated locally and is NOT committed (see .gitignore). Whether it
may be shared with the assignment depends on the course data-use permission;
generating it locally and sharing it publicly are separate questions.

Code and output labels are in English.
"""

import csv
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import card_common
from replicate_table4 import make_gap, qualifies_primary, qualifies_supplementary

PROCESSED_DIR = os.path.join(card_common.PROJECT_ROOT, "data", "processed")
CSV_PATH = os.path.join(PROCESSED_DIR, "store_level.csv")

# Raw columns, in DATA_DICTIONARY order. SHEET and STATUS2 stay strings; the
# rest are parsed to numbers (blank when missing).
RAW_COLUMNS = [
    "SHEET", "CHAIN", "CO_OWNED", "STATE", "SOUTHJ", "CENTRALJ", "PA1", "PA2",
    "EMPFT", "EMPPT", "NMGRS", "WAGE_ST", "BONUS", "HRSOPEN", "PSODA", "PFRY",
    "PENTREE", "STATUS2", "EMPFT2", "EMPPT2", "NMGRS2", "WAGE_ST2", "SPECIAL2",
    "HRSOPEN2", "PSODA2", "PFRY2", "PENTREE2",
]

INT_COLUMNS = {
    "CHAIN", "CO_OWNED", "STATE", "SOUTHJ", "CENTRALJ", "PA1", "PA2",
    "BONUS", "SPECIAL2",
}

CONSTRUCTED = [
    "fte_before", "fte_after", "fte_after_temp0", "change_fte", "gap",
]

MARKERS = [
    "sample_table3_balanced",
    "sample_table3_temp0",
    "sample_table4_primary",
    "sample_table4_supplementary",
    "sample_extension_excl_closures",
]

HEADER = RAW_COLUMNS + CONSTRUCTED + MARKERS


def _fmt_float(v):
    return "" if v is None else f"{v:.8g}"


def _fmt_int(v):
    return "" if v is None else str(int(v))


def _raw_cell(row, key):
    """Format one raw column for the CSV (verbatim strings, parsed numbers)."""
    raw = row[key].strip()
    if key in ("SHEET", "STATUS2"):
        return raw
    value = card_common.parse_float(raw)
    if value is None:
        return ""
    if key in INT_COLUMNS:
        return str(int(value))
    return _fmt_float(value)


def main():
    rows = []
    with open(card_common.DATA_PATH, newline="") as f:
        for row in csv.DictReader(f):
            state = card_common.parse_float(row["STATE"])
            if state is None or int(state) not in (0, 1):
                continue
            rows.append(row)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    marker_sums = {m: 0 for m in MARKERS}

    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for row in rows:
            fb = card_common.compute_fte_before(row)
            fa = card_common.compute_fte_after(row)
            fa_t0 = card_common.compute_fte_after(row, temp_closed_to_zero=True)

            balanced = fb is not None and fa is not None
            temp0 = fb is not None and fa_t0 is not None
            status2 = row["STATUS2"].strip()
            change = (fa - fb) if balanced else None

            markers = {
                "sample_table3_balanced": balanced,
                "sample_table3_temp0": temp0,
                "sample_table4_primary": qualifies_primary(row),
                "sample_table4_supplementary": qualifies_supplementary(row),
                "sample_extension_excl_closures": balanced and status2 != "3",
            }

            constructed = [
                _fmt_float(fb),
                _fmt_float(fa),
                _fmt_float(fa_t0),
                _fmt_float(change),
                _fmt_float(make_gap(row)),
            ]

            marker_cells = []
            for m in MARKERS:
                flag = markers[m]
                marker_sums[m] += 1 if flag else 0
                marker_cells.append("1" if flag else "0")

            writer.writerow(
                [_raw_cell(row, k) for k in RAW_COLUMNS]
                + constructed
                + marker_cells
            )

    print("=== Restaurant-level processed data export ===\n")
    print(f"Records written: {len(rows)}")
    print("Sample-marker counts:")
    for m in MARKERS:
        print(f"  {m}: {marker_sums[m]}")
    print("Wrote", CSV_PATH)


if __name__ == "__main__":
    main()
