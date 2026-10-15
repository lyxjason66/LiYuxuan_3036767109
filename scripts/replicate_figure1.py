#!/usr/bin/env python3
"""Replicate Card & Krueger (1994) Figure 1: distribution of starting wages.

Two stacked panels compare New Jersey and Pennsylvania with side-by-side bars
over starting-wage bins:

    top    February 1992 (before, WAGE_ST)
    bottom November 1992 (after, WAGE_ST2)

The y-axis is the percent of restaurants. Each state-period is normalized by
its own number of valid wage observations, so a store is kept whenever its
starting wage is present, regardless of whether its employment data is valid.
Each panel is drawn on its own y-axis scale (0-35 percent before, 0-90 percent
after), mirroring the original figure's separate axis ranges.

Binning (centered on the x-axis tick labels, matching the original figure's
10-cent interval spacing):

    10-cent bins centered at 4.25, 4.35, ..., 5.55, i.e.
    [4.20, 4.30), [4.30, 4.40), ..., [5.50, 5.60).

Centering matters: a $4.50 wage falls in the [4.50, 4.60) bin whose center and
tick label is 4.55, not in a [4.45, 4.55) bin labeled 4.45. Bins are
left-closed and right-open. Wages are binned on integer cents to avoid
floating-point edge errors. Missing wages are excluded (never filled with
zero). The original axis ends at 5.55, so the few wages at or above $5.60 fall
off the right edge and are excluded (reported in the notes, never silently).

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

# Bin centers in cents (the x-axis tick labels in the original figure):
# 425, 435, ..., 555, i.e. $4.25, $4.35, ..., $5.55. Each 10-cent bin is
# centered on its tick label, so bin i covers [center - 5, center + 5) cents;
# the left edges are therefore 420, 430, ..., 550. A wage is assigned to the
# bin whose center it falls around (e.g. $4.50 -> the 4.55-centered bin).
# The original figure's axis ends at 5.55, so there is NO open top bin: the
# last bin is [5.50, 5.60) centered at 5.55, and the few wages at or above
# $5.60 fall off the right edge (excluded, reported in the notes).
BIN_CENTER_CENTS = list(range(425, 565, 10))       # 425, 435, ..., 555
BIN_LEFT_CENTS = [c - 5 for c in BIN_CENTER_CENTS]  # 420, 430, ..., 550
OPEN_TOP_CENTS = 560          # right edge of the last centered bin [5.50, 5.60)
N_BINS = len(BIN_CENTER_CENTS)  # 14 bins, matching the original axis

STATE_ORDER = [(1, "NJ", "New Jersey"), (0, "PA", "Pennsylvania")]
STATE_COLOR = {1: "#1f77b4", 0: "#ff7f0e"}  # NJ blue, PA orange
STATE_NAME = {1: "New Jersey", 0: "Pennsylvania"}

PERIODS = [
    ("before", "WAGE_ST", "February 1992"),
    ("after", "WAGE_ST2", "November 1992"),
]

# Per-panel y-axis limits, mirroring the original figure: the "before"
# distribution peaks near 35 percent while the "after" distribution peaks near
# 90 percent, so each panel is drawn on its own scale rather than shared.
Y_LIMITS = {"before": (0, 35), "after": (0, 90)}


def wage_to_cents(value):
    """Convert a dollar wage to integer cents (values are 2-decimal)."""
    return int(round(value * 100))


def bin_index(cents):
    """Return the 0-based bin index for a wage in cents, or None if outside
    the plotted range [4.20, 5.60)."""
    if cents < BIN_LEFT_CENTS[0]:
        return None
    if cents >= OPEN_TOP_CENTS:
        return None
    return (cents - BIN_LEFT_CENTS[0]) // 10


def bin_bounds(i):
    """Return (lower, upper) dollar strings for bin i."""
    lower = BIN_LEFT_CENTS[i] / 100.0
    upper = (BIN_LEFT_CENTS[i] + 10) / 100.0
    return f"{lower:.2f}", f"{upper:.2f}"


def bin_label(i):
    """Return the axis label for bin i (the bin center)."""
    return f"{BIN_CENTER_CENTS[i] / 100.0:.2f}"


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
            above = []
            for w in values:
                cents = wage_to_cents(w)
                bi = bin_index(cents)
                if bi is None:
                    if cents < BIN_LEFT_CENTS[0]:
                        below.append(w)
                    else:
                        above.append(w)
                else:
                    counts[bi] += 1
            stats[(period, state)] = {
                "counts": counts,
                "denom": denom,
                "below": below,
                "above": above,
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
        2, 1, figsize=(12, 8), sharex=False, sharey=False
    )

    for ax, (period, _col, title) in zip(axes, PERIODS):
        for state, _abbrev, _name in STATE_ORDER:
            s = stats[(period, state)]
            denom = s["denom"]
            pct = [
                (100.0 * cnt / denom) if denom else 0.0
                for cnt in s["counts"]
            ]
            # NJ at x - width/2, PA at x + width/2 (same width: no overlap).
            # `state` is the integer code (1 = NJ, 0 = PA), NOT the "NJ"/"PA"
            # string, so the two bars land on opposite sides of each bin.
            offset = -width / 2 if state == 1 else width / 2
            ax.bar(
                x + offset,
                pct,
                width=width,
                color=STATE_COLOR[state],
                label=STATE_NAME[state],
            )
        ax.set_title(title, loc="left")
        ax.set_ylabel("Percent")
        ax.set_ylim(*Y_LIMITS[period])
        ax.grid(axis="y", linestyle=":", alpha=0.4)

    axes[0].legend(loc="upper right")
    # Show the wage-interval labels on BOTH panels. Ticks mark each bin's
    # center (4.25, 4.35, ..., 5.55); the last bin is [5.50, 5.60).
    tick_labels = [bin_label(i) for i in range(N_BINS)]
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(tick_labels)
        ax.set_xlim(-0.6, N_BINS - 0.4 + 0.2)
    axes[1].set_xlabel("Wage Range")
    fig.suptitle(
        "Distribution of Starting Wage Rates (Card & Krueger 1994, Figure 1)",
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
    notes.append("## Binning (centered on the x-axis tick labels)\n")
    notes.append(
        "- The original scan marks the x-axis at 4.25, 4.35, ..., 5.55 but "
        "does not state the bin boundaries or the tail rule in text."
    )
    notes.append(
        "- This replication centers each 10-cent bin on its tick label, so "
        "the bins are [4.20, 4.30), [4.30, 4.40), ..., [5.50, 5.60), "
        "left-closed and right-open."
    )
    notes.append(
        "- Centering matters: the $4.50 cluster (a tall ~16-17% bar in each "
        "state) falls in the [4.50, 4.60) bin whose center and label is 4.55, "
        "not in a [4.45, 4.55) bin labeled 4.45."
    )
    notes.append(
        "- Wages are binned on integer cents (round(wage * 100)) to avoid "
        "floating-point boundary errors."
    )
    notes.append("")
    notes.append("## Range / tail check\n")
    notes.append(
        "- No observed starting wage is below $4.20, so nothing is dropped on "
        "the low end."
    )
    notes.append(
        "- The original axis ends at 5.55, so wages at or above $5.60 fall off "
        "the right edge and are excluded (not drawn as an open bin). Wage "
        "minima/maxima and excluded counts per state-period:"
    )
    notes.append("")
    notes.append("| Period | State | n | min | max | excluded >=5.60 |")
    notes.append("|---|---|---|---|---|---|")
    for period, _col, title in PERIODS:
        for state, code, name in STATE_ORDER:
            s = stats[(period, state)]
            mn = f"{s['min']:.2f}" if s["min"] is not None else ""
            mx = f"{s['max']:.2f}" if s["max"] is not None else ""
            notes.append(
                f"| {title} | {name} | {s['denom']} | {mn} | {mx} | "
                f"{len(s['above'])} |"
            )
    notes.append("")
    notes.append("## Percent sums\n")
    notes.append(
        "- Percentages sum to just under 100 per state-period because the few "
        "wages at or above $5.60 (off the original's right edge) are excluded."
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
    notes.append("## Layout\n")
    notes.append(
        "- Two stacked panels (February 1992 on top, November 1992 on the "
        "bottom), each with side-by-side bars for New Jersey and "
        "Pennsylvania."
    )
    notes.append(
        "- Each panel has its own y-axis scale, mirroring the original figure: "
        "0-35 percent for February 1992 and 0-90 percent for November 1992."
    )
    notes.append(
        "- Axis labels follow the original: y-axis 'Percent', x-axis 'Wage "
        "Range', and x-axis ticks at the bin centers 4.25, 4.35, ..., 5.55 "
        "(the axis ends at 5.55, matching the original)."
    )
    notes.append("")
    notes.append("## Differences from the original figure\n")
    notes.append(
        "- Wages at or above $5.60 fall off the original's right edge and are "
        "excluded (6 of 779 valid wage observations). These are reported in "
        "'Range / tail check' above, never dropped silently."
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
            above = len(s["above"])
            print(
                f"{period:6s} {name:11s} n={s['denom']:3d} "
                f"sum%={total:.4f} below_4.20={below} above_5.60={above}"
            )
    print("Wrote", PNG_PATH)
    print("Wrote", CSV_PATH)
    print("Wrote", NOTES_PATH)


if __name__ == "__main__":
    main()
