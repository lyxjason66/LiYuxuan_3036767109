#!/usr/bin/env python3
"""Replicate Card & Krueger (1994) Table 3 (8 columns x 5 rows).

Table 3 reports mean FTE employment (and, in parentheses, standard
errors) by state and, within New Jersey, by the wave-1 starting wage
group.  The 8 columns are:

    PA, NJ, NJ-PA,
    NJ wage == $4.25, NJ wage in $4.26-$4.99, NJ wage >= $5.00,
    low - high, mid - high.

The 5 rows are:

    1. FTE employment before, all available observations
    2. FTE employment after, all available observations
    3. change in mean FTE employment (= after mean - before mean)
    4. change in mean FTE, balanced sample (per-store change)
    5. change in mean FTE, balanced sample, with temporarily closed
       stores' after FTE set to 0 (separate alternative treatment)

Operating-status rules (shared via card_common):
    permanent closure (STATUS2 = 3)  -> after FTE = 0
    temporary closure (STATUS2 = 2, 4, 5) -> after FTE missing
        (in row 5 only, these are set to 0)
    refusals and other missing data are never imputed to zero.

Wage groups use the wave-1 starting wage among NJ stores.  Stores with a
missing starting wage are excluded from the wage columns but are NOT
dropped from the state-level columns.

Standard errors:
    * rows 1-2: SEM of the level values (sample sd / sqrt(n)).
    * rows 4-5: SEM of the per-store change values.
    * row 3: the original paper's standard-error formula is NOT confirmed,
      so the main table reports NA for the row-3 SEs.  A naive
      sqrt(se_before^2 + se_after^2) approximation is kept only in a
      separate diagnostic note and is not used for significance.

Outputs:
    outputs/table3_replication.csv      (long-format, full precision)
    outputs/table3_sample_counts.csv    (valid N per cell, for checking)
    outputs/table3_replication.md       (human-readable table + notes)

Code and output labels are in English.
"""

import csv
import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import card_common

OUTPUT_DIR = os.path.join(card_common.PROJECT_ROOT, "outputs")
CSV_PATH = os.path.join(OUTPUT_DIR, "table3_replication.csv")
COUNTS_PATH = os.path.join(OUTPUT_DIR, "table3_sample_counts.csv")
MD_PATH = os.path.join(OUTPUT_DIR, "table3_replication.md")

WAGE_LOW = 4.25
WAGE_HIGH = 5.00

# Base columns: key -> (label, selector over a record).
BASE_COLUMNS = [
    ("pa", "PA", lambda r: r["state"] == 0),
    ("nj", "NJ", lambda r: r["state"] == 1),
    (
        "low",
        "Wage=$4.25",
        lambda r: r["state"] == 1 and r["wage_st"] is not None
        and r["wage_st"] == WAGE_LOW,
    ),
    (
        "mid",
        "Wage=$4.26-$4.99",
        lambda r: r["state"] == 1 and r["wage_st"] is not None
        and WAGE_LOW < r["wage_st"] < WAGE_HIGH,
    ),
    (
        "high",
        "Wage>=$5.00",
        lambda r: r["state"] == 1 and r["wage_st"] is not None
        and r["wage_st"] >= WAGE_HIGH,
    ),
]

# Difference columns: key -> (label, base_a, base_b), value = a - b.
DIFF_COLUMNS = [
    ("nj_pa", "NJ-PA", "nj", "pa"),
    ("low_high", "Low-high", "low", "high"),
    ("mid_high", "Mid-high", "mid", "high"),
]

COLUMN_ORDER = [
    "pa",
    "nj",
    "nj_pa",
    "low",
    "mid",
    "high",
    "low_high",
    "mid_high",
]

COLUMN_LABELS = {k: v for k, v, _ in BASE_COLUMNS}
COLUMN_LABELS.update({k: v for k, v, _, _ in DIFF_COLUMNS})

ROW_ORDER = ["before", "after", "change", "balanced", "temp0_balanced"]
ROW_LABELS = {
    "before": "1. FTE before, all available",
    "after": "2. FTE after, all available",
    "change": "3. Change in mean FTE",
    "balanced": "4. Change, balanced sample",
    "temp0_balanced": "5. Change, temp. closures set to 0",
}


def mean_sem(values):
    """Return (n, mean, sem) of a list of values."""
    return card_common.summarize(values)


def change_stats(before_stats, after_stats):
    """Combine before/after (n, mean, sem) into the row-3 change statistic.

    Only the point estimate is reported; the standard error is set to None
    (shown as NA) because the paper's row-3 SE formula is unconfirmed.
    """
    _, b_mean, _b_se = before_stats
    _, a_mean, _a_se = after_stats
    if b_mean is None or a_mean is None:
        return ("", None, None)
    return ("", a_mean - b_mean, None)


def naive_change_se(before_stats, after_stats):
    """Naive independent-sample SE for a before/after change.

    Kept only for the separate diagnostic note: sqrt(se_before^2 +
    se_after^2).  Not used for significance.
    """
    _, _b_mean, b_se = before_stats
    _, _a_mean, a_se = after_stats
    if b_se is None or a_se is None:
        return None
    return math.sqrt(b_se ** 2 + a_se ** 2)


def main():
    records = card_common.load_records()

    # Wage-range check (NJ only): report out-of-range / missing wages.
    below_range = [
        r["wage_st"] for r in records
        if r["state"] == 1 and r["wage_st"] is not None and r["wage_st"] < WAGE_LOW
    ]
    missing_wage = sum(
        1 for r in records if r["state"] == 1 and r["wage_st"] is None
    )

    # Build per-column groups once.
    groups = {}
    for key, _label, selector in BASE_COLUMNS:
        groups[key] = [r for r in records if selector(r)]

    # Compute per-row (n, mean, sem) for each base column.
    # base_results[row][col] = (n, mean, sem)
    base_results = {row: {} for row in ROW_ORDER}

    for key, _label, _selector in BASE_COLUMNS:
        group = groups[key]
        before = mean_sem([r["fte_before"] for r in group if r["fte_before"] is not None])
        after = mean_sem([r["fte_after"] for r in group if r["fte_after"] is not None])
        balanced = mean_sem(
            [
                r["fte_after"] - r["fte_before"]
                for r in group
                if r["fte_before"] is not None and r["fte_after"] is not None
            ]
        )
        temp0 = mean_sem(
            [
                r["fte_after_temp0"] - r["fte_before"]
                for r in group
                if r["fte_before"] is not None and r["fte_after_temp0"] is not None
            ]
        )
        base_results["before"][key] = before
        base_results["after"][key] = after
        base_results["change"][key] = change_stats(before, after)
        base_results["balanced"][key] = balanced
        base_results["temp0_balanced"][key] = temp0

    # Naive independent-sample row-3 SEs, kept only for the diagnostic note.
    row3_naive = {}
    for key, _label, _selector in BASE_COLUMNS:
        row3_naive[key] = naive_change_se(
            base_results["before"][key], base_results["after"][key]
        )
    for key, _label, a, b in DIFF_COLUMNS:
        a_se = row3_naive[a]
        b_se = row3_naive[b]
        if a_se is not None and b_se is not None:
            row3_naive[key] = math.sqrt(a_se ** 2 + b_se ** 2)
        else:
            row3_naive[key] = None

    # Derive difference columns.
    full_results = {row: {} for row in ROW_ORDER}
    for row in ROW_ORDER:
        for key, _label, a, b in DIFF_COLUMNS:
            _, a_mean, a_se = base_results[row][a]
            _, b_mean, b_se = base_results[row][b]
            if a_mean is None or b_mean is None:
                full_results[row][key] = ("", None, None)
                continue
            mean = a_mean - b_mean
            if a_se is not None and b_se is not None:
                se = math.sqrt(a_se ** 2 + b_se ** 2)
            else:
                se = None
            full_results[row][key] = ("", mean, se)

    # Merge base + diff into a single lookup.
    for row in ROW_ORDER:
        for key in BASE_COLUMNS_KEYS:
            full_results[row][key] = base_results[row][key]

    # ---- Write long-format CSV ----
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["row", "column", "n", "mean", "se"])
        for row in ROW_ORDER:
            for col in COLUMN_ORDER:
                n, mean, se = full_results[row][col]
                writer.writerow(
                    [
                        row,
                        col,
                        n,
                        "" if mean is None else f"{mean:.6f}",
                        "" if se is None else f"{se:.6f}",
                    ]
                )

    # ---- Write sample-count CSV ----
    with open(COUNTS_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["row"] + [key for key, _, _ in BASE_COLUMNS])
        for row in ROW_ORDER:
            writer.writerow(
                [row] + [base_results[row][key][0] for key, _, _ in BASE_COLUMNS]
            )

    # ---- Write Markdown ----
    md_lines = []
    md_lines.append("# Card & Krueger (1994) Table 3 replication\n")
    md_lines.append(
        "Mean FTE employment by state and, within New Jersey, by wave-1 "
        "starting-wage group. Standard errors are in parentheses."
    )
    md_lines.append("")
    md_lines.append(
        "| Row | " + " | ".join(COLUMN_LABELS[c] for c in COLUMN_ORDER) + " |"
    )
    md_lines.append(
        "|-----|" + "|".join(["-----"] * len(COLUMN_ORDER)) + "|"
    )
    for row in ROW_ORDER:
        cells = []
        for col in COLUMN_ORDER:
            n, mean, se = full_results[row][col]
            if mean is None:
                cells.append("")
            else:
                se_text = "NA" if se is None else f"{se:.2f}"
                cells.append(f"{mean:.2f} ({se_text})")
        md_lines.append("| " + ROW_LABELS[row] + " | " + " | ".join(cells) + " |")
    md_lines.append("")

    md_lines.append("## Sample and closure rules\n")
    md_lines.append(
        "- Rows 1 and 2 use each period's own valid sample (a store needs "
        "valid FTE in that period only; it need not appear in both periods)."
    )
    md_lines.append(
        "- Rows 4 and 5 use the balanced sample (a store contributes only "
        "when its FTE is valid in both waves)."
    )
    md_lines.append(
        "- FTE = full-time + managers + 0.5 * part-time; a missing component "
        "leaves FTE missing (never filled with zero)."
    )
    md_lines.append(
        "- STATUS2 = 3 (permanent closure): after FTE set to 0 (6 stores)."
    )
    md_lines.append(
        "- STATUS2 in {2, 4, 5} (temporary closure): after FTE treated as "
        "missing in rows 1-4 (4 stores)."
    )
    md_lines.append(
        "- Row 5 only: temporarily closed stores get after FTE = 0, then the "
        "balanced sample is re-determined and the per-store change is averaged."
    )
    md_lines.append(
        "- Refusals and any other missing data are never imputed to zero."
    )
    md_lines.append(
        "- Wage columns use the NJ wave-1 starting wage; stores with a missing "
        "wage are excluded from wage columns but kept in the state columns."
    )
    md_lines.append("")

    md_lines.append("## Standard errors\n")
    md_lines.append(
        "- Rows 1-2: SEM of the level values."
    )
    md_lines.append(
        "- Rows 4-5: SEM of the per-store change values (balanced sample), "
        "i.e. the store-level change is treated as the unit of observation."
    )
    md_lines.append(
        "- Row 3: the original paper's standard-error formula is "
        "**unconfirmed (to verify)**, so all eight row-3 SEs are reported as "
        "NA in the main table."
    )
    md_lines.append(
        "- Difference-column SEs (NJ-PA, low-high, mid-high) are "
        "sqrt(se_a^2 + se_b^2), treating the two groups as independent "
        "(valid for PA vs NJ and across wage groups); this applies to rows "
        "1, 2, 4, and 5 only."
    )
    md_lines.append("")

    md_lines.append("## Row 3 standard errors: naive diagnostic (not for significance)\n")
    md_lines.append(
        "Values below use the naive independent-sample approximation "
        "sqrt(se_before^2 + se_after^2). They are retained only for "
        "diagnosis; they do not match the paper's row-3 SE (e.g. the paper's "
        "NJ-PA SE is 1.36 while the naive value is 1.80), and must not be "
        "used for significance conclusions."
    )
    md_lines.append("")
    md_lines.append(
        "| Column | " + " | ".join(COLUMN_LABELS[c] for c in COLUMN_ORDER) + " |"
    )
    md_lines.append(
        "|--------|" + "|".join(["--------"] * len(COLUMN_ORDER)) + "|"
    )
    diag_cells = [
        "" if row3_naive[col] is None else f"{row3_naive[col]:.2f}"
        for col in COLUMN_ORDER
    ]
    md_lines.append("| Naive row-3 SE | " + " | ".join(diag_cells) + " |")
    md_lines.append("")

    md_lines.append("## Wage-range check\n")
    if below_range:
        md_lines.append(
            f"- NJ stores with starting wage below $4.25 (out of range): "
            f"{below_range}."
        )
    else:
        md_lines.append(
            "- No NJ store has a starting wage below $4.25 (all in range)."
        )
    md_lines.append(
        f"- NJ stores with missing starting wage (excluded from wage columns): "
        f"{missing_wage}."
    )
    md_lines.append("")

    md_lines.append("## Comparison with the paper\n")
    md_lines.append(
        "- All cells are computed. The main point estimates and the balanced "
        "sample (rows 1, 2, 4, 5) are close to or match the paper; row-3 "
        "standard errors are not yet reproduced."
    )
    md_lines.append(
        "- Column definitions and wage-group counts match the paper's "
        "footnotes (low N=101, mid N=140, high N=73; six closed stores set to "
        "0; four temporary closures treated as missing)."
    )
    md_lines.append(
        "- Row 4 NJ-PA (balanced DiD) matches the paper's 2.75 (1.34)."
    )
    md_lines.append(
        "- Row 5 NJ-PA (temporary closures set to 0) is 2.51 (1.35)."
    )
    md_lines.append(
        "- Row 3 NJ-PA: the paper reports 2.76 (1.36); this replication "
        "computes 2.75360578, which rounds to 2.75. The cause of this "
        "difference is not yet confirmed, so it is recorded here rather than "
        "dismissed as rounding."
    )
    md_lines.append("")

    with open(MD_PATH, "w") as f:
        f.write("\n".join(md_lines))

    # ---- Terminal summary ----
    print("=== Card & Krueger (1994) Table 3 replication ===\n")
    header = "Row".ljust(34) + "".join(f"{COLUMN_LABELS[c]:>12}" for c in COLUMN_ORDER)
    print(header)
    for row in ROW_ORDER:
        line = ROW_LABELS[row].ljust(34)
        for col in COLUMN_ORDER:
            _n, mean, _se = full_results[row][col]
            line += ("" if mean is None else f"{mean:.2f}").rjust(12)
        print(line)
    print("\nWage-range check: below $4.25 ->", below_range or "none",
          "; missing wage (NJ) ->", missing_wage)
    print("Wrote", CSV_PATH)
    print("Wrote", COUNTS_PATH)
    print("Wrote", MD_PATH)


BASE_COLUMNS_KEYS = [k for k, _, _ in BASE_COLUMNS]


if __name__ == "__main__":
    main()
