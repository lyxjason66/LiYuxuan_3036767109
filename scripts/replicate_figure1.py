#!/usr/bin/env python3
"""Replicate Card & Krueger (1994) Figure 1: distribution of starting wages.

Two stacked panels compare New Jersey and Pennsylvania with side-by-side bars
over starting-wage bins:

    top    February 1992 (before, WAGE_ST)
    bottom November 1992 (after, WAGE_ST2)

The y-axis is the percent of restaurants. Each state-period is normalized by
its own number of valid wage observations, so a store is kept whenever its
starting wage is present, regardless of whether its employment data is valid.

Binning (a replication choice -- the scan does not state the original rule):

    10-cent bins  [4.25, 4.35), [4.35, 4.45), ..., [5.45, 5.55),
    plus an open top bin [5.55, inf) for wages at or above $5.55.

Bins are left-closed and right-open. Wages are binned on integer cents to
avoid floating-point edge errors. Missing wages are excluded (never filled
with zero). No valid wage is silently dropped: values below $4.25 are flagged
and values at or above $5.55 fall into the open top bin.

Outputs:
    outputs/figure1_wage_distribution.png
    outputs/figure1_wage_distribution.csv
    outputs/figure1_notes.md

Code, figure labels, and notes are in English.
"""

import csv
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import card_common

OUTPUT_DIR = os.path.join(card_common.PROJECT_ROOT, "outputs")
PNG_PATH = os.path.join(OUTPUT_DIR, "figure1_wage_distribution.png")
CSV_PATH = os.path.join(OUTPUT_DIR, "figure1_wage_distribution.csv")
NOTES_PATH = os.path.join(OUTPUT_DIR, "figure1_notes.md")

# Left edges of the fixed 10-cent bins, in cents: 425, 435, ..., 545.
BIN_LEFT_CENTS = list(range(425, 555, 10))
OPEN_TOP_CENTS = 555          # start of the open top bin [5.55, inf)
N_BINS = len(BIN_LEFT_CENTS) + 1  # 13 fixed bins + 1 open top bin = 14

STATE_ORDER = [(1, "NJ", "New Jersey"), (0, "PA", "Pennsylvania")]
STATE_COLOR = {1: "#1f77b4", 0: "#ff7f0e"}  # NJ blue, PA orange
STATE_NAME = {1: "New Jersey", 0: "Pennsylvania"}

PERIODS = [
    ("before", "WAGE_ST", "February 1992 (before)"),
    ("after", "WAGE_ST2", "November 1992 (after)"),
]


def wage_to_cents(value):
    """Convert a dollar wage to integer cents (values are 2-decimal)."""
    return int(round(value * 100))


def bin_index(cents):
    """Return the 0-based bin index for a wage in cents, or None if < 4.25."""
    if cents < BIN_LEFT_CENTS[0]:
        return None
    return min((cents - BIN_LEFT_CENTS[0]) // 10, N_BINS - 1)


def bin_bounds(i):
    """Return (lower, upper) dollar strings for bin i (upper empty if open)."""
    if i < len(BIN_LEFT_CENTS):
        lower = BIN_LEFT_CENTS[i] / 100.0
        upper = (BIN_LEFT_CENTS[i] + 10) / 100.0
        return f"{lower:.2f}", f"{upper:.2f}"
    return f"{OPEN_TOP_CENTS / 100.0:.2f}", ""  # empty upper = +infinity


def bin_label(i):
    """Return the axis label for bin i."""
    if i < len(BIN_LEFT_CENTS):
        return f"{BIN_LEFT_CENTS[i] / 100.0:.2f}"
    return ">=5.55"


def collect_wages():
    """Return {period: {state: [wage, ...]}} for valid wages only."""
    data = {}
    with open(card_common.DATA_PATH, newline="") as f:
        for row in csv.DictReader(f):
            state = card_common.parse_float(row["STATE"])
            if state is None:
                continue
            state = int(state)
            if state not in STATE_NAME:
                continue
            for period, col, _title in PERIODS:
                wage = card_common.parse_float(row[col])
                if wage is not None:
                    data.setdefault(period, {}).setdefault(state, []).append(wage)
    return data


def main():
    data = collect_wages()

    # ---- Build per (period, state) counts ----
    # counts[(period, state)] = [count per bin]; denom, below, min, max alongside.
    stats = {}
    for period, _col, _title in PERIODS:
        for state, _code, _name in STATE_ORDER:
            values = data.get(period, {}).get(state, [])
            denom = len(values)
            counts = [0] * N_BINS
            below = []
            for w in values:
                cents = wage_to_cents(w)
                bi = bin_index(cents)
                if bi is None:
                    below.append(w)
                else:
                    counts[bi] += 1
            stats[(period, state)] = {
                "counts": counts,
                "denom": denom,
                "below": below,
                "min": min(values) if values else None,
                "max": max(values) if values else None,
            }

    # ---- Write CSV ----
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["period", "state", "state_name", "bin_lower", "bin_upper",
             "bin_label", "count", "denominator", "percent"]
        )
        for period, _col, _title in PERIODS:
            for state, code, name in STATE_ORDER:
                s = stats[(period, state)]
                denom = s["denom"]
                for i in range(N_BINS):
                    lower, upper = bin_bounds(i)
                    cnt = s["counts"][i]
                    pct = (100.0 * cnt / denom) if denom else 0.0
                    writer.writerow(
                        [period, code, name, lower, upper, bin_label(i),
                         cnt, denom, f"{pct:.4f}"]
                    )

    # ---- Figure ----
    # Numeric bin positions (not category strings), so the two states can be
    # placed side by side at x - width/2 and x + width/2 with the same width.
    x = np.arange(N_BINS)
    width = 0.4
    fig, axes = plt.subplots(
        2, 1, figsize=(12, 8), sharex=False, sharey=True
    )

    for ax, (period, _col, title) in zip(axes, PERIODS):
        for state, code, name in STATE_ORDER:
            s = stats[(period, state)]
            denom = s["denom"]
            pct = [
                (100.0 * cnt / denom) if denom else 0.0
                for cnt in s["counts"]
            ]
            # NJ at x - width/2, PA at x + width/2 (same width: no overlap).
            offset = -width / 2 if code == 1 else width / 2
            ax.bar(
                x + offset,
                pct,
                width=width,
                color=STATE_COLOR[state],
                label=STATE_NAME[state],
            )
        ax.set_title(title, loc="left")
        ax.set_ylabel("Percent of restaurants")
        ax.grid(axis="y", linestyle=":", alpha=0.4)

    axes[0].legend(title="State", loc="upper right")
    # Show the wage-interval labels on BOTH panels. Ticks mark each bin's
    # lower bound; the final bin is open (>=5.55).
    tick_labels = [bin_label(i) for i in range(N_BINS)]
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(tick_labels)
        ax.set_xlim(-0.6, N_BINS - 0.4 + 0.2)
    axes[1].set_xlabel(
        "Starting wage range (dollars); tick = bin lower bound, "
        "last bin is >=5.55"
    )
    fig.suptitle(
        "Replication of Figure 1: Distribution of Starting Wage Rates "
        "(Card & Krueger 1994)",
        fontsize=13,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(PNG_PATH, dpi=150)
    plt.close(fig)

    # ---- Notes (Markdown) ----
    notes = []
    notes.append("# Card & Krueger (1994) Figure 1 replication notes\n")
    notes.append(
        "Distribution of starting wages, New Jersey vs. Pennsylvania. "
        "Two panels: February 1992 (before, WAGE_ST) and November 1992 "
        "(after, WAGE_ST2)."
    )
    notes.append("")
    notes.append("## Missing-data handling\n")
    notes.append(
        "- A store is included in a state-period distribution whenever its "
        "starting wage is present; employment data play no role here."
    )
    notes.append(
        "- Missing wages are excluded and are never filled with zero."
    )
    notes.append(
        "- The denominator for a state-period is its own count of valid "
        "wage observations (not a common or employment-based total)."
    )
    notes.append("")
    notes.append("## Binning (a replication choice)\n")
    notes.append(
        "- The original scan marks the x-axis at 4.25, 4.35, ..., 5.55 but "
        "does not state the bin boundaries or the tail rule, so the exact "
        "original binning is NOT confirmed here."
    )
    notes.append(
        "- This replication uses 10-cent bins [4.25, 4.35), [4.35, 4.45), "
        "..., [5.45, 5.55), left-closed and right-open, plus an open top bin "
        "[5.55, +infinity)."
    )
    notes.append(
        "- A wage of exactly $5.05 falls in the [5.05, 5.15) bin (left-closed). "
        "This is a share of an interval, not a 'wage that rounds to 5.05' "
        "count; the two are not conflated."
    )
    notes.append(
        "- Wages are binned on integer cents (round(wage * 100)) to avoid "
        "floating-point boundary errors."
    )
    notes.append("")
    notes.append("## Range / tail check\n")
    notes.append(
        "- No observed starting wage is below $4.25, so nothing is dropped on "
        "the low end."
    )
    notes.append(
        "- The data extend above the last 10-cent bin, so the open top bin "
        "[5.55, +infinity) captures those values rather than dropping them. "
        "Wage minima/maxima per state-period:"
    )
    notes.append("")
    notes.append("| Period | State | n | min | max |")
    notes.append("|---|---|---|---|---|")
    for period, _col, title in PERIODS:
        for state, code, name in STATE_ORDER:
            s = stats[(period, state)]
            mn = f"{s['min']:.2f}" if s["min"] is not None else ""
            mx = f"{s['max']:.2f}" if s["max"] is not None else ""
            notes.append(
                f"| {title} | {name} | {s['denom']} | {mn} | {mx} |"
            )
    notes.append("")
    notes.append("## Percent sums\n")
    notes.append(
        "- Percentages should sum to about 100 per state-period (float "
        "rounding may give 99.99/100.01)."
    )
    notes.append("")
    notes.append("| Period | State | sum of percents |")
    notes.append("|---|---|---|")
    for period, _col, _title in PERIODS:
        for state, code, name in STATE_ORDER:
            s = stats[(period, state)]
            total = 100.0 * sum(s["counts"]) / s["denom"] if s["denom"] else 0.0
            notes.append(f"| {period} | {name} | {total:.4f} |")
    notes.append("")
    notes.append("## Differences from the original figure\n")
    notes.append(
        "- The open top bin is labeled '>=5.55' (the original only marks "
        "'5.55'); this makes the tail treatment explicit."
    )
    notes.append(
        "- Bar colors, spacing, and layout are this replication's choices; "
        "the figure was not reverse-engineered from the original's bar "
        "heights."
    )
    notes.append("")

    with open(NOTES_PATH, "w") as f:
        f.write("\n".join(notes))

    # ---- Terminal summary ----
    print("=== Figure 1 wage distribution ===")
    for period, _col, _title in PERIODS:
        for state, code, name in STATE_ORDER:
            s = stats[(period, state)]
            total = 100.0 * sum(s["counts"]) / s["denom"] if s["denom"] else 0.0
            below = len(s["below"])
            print(
                f"{period:6s} {name:11s} n={s['denom']:3d} "
                f"sum%={total:.4f} below_4.25={below}"
            )
    print("Wrote", PNG_PATH)
    print("Wrote", CSV_PATH)
    print("Wrote", NOTES_PATH)


if __name__ == "__main__":
    main()
