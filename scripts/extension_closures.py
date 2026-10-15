#!/usr/bin/env python3
"""Sensitivity check: exclude permanently closed restaurants from Table 3 row 4.

Research question: is the New Jersey vs. Pennsylvania difference in the
per-store change in full-time-equivalent employment still similar when the
permanently closed restaurants are dropped?

Two samples are compared (both re-use card_common's FTE rules; nothing in the
base replication scripts or the raw data is modified):

    baseline                    the Table 3 row-4 balanced sample: a store is
                                kept when FTE is valid in both waves, where a
                                permanently closed store (STATUS2 = 3) has
                                after-FTE = 0 and a temporarily closed store
                                has after-FTE missing (so it is excluded).
    excluding_permanent_closures  the baseline sample minus the stores with
                                STATUS2 = 3.  All other missing-value and
                                temporary-closure rules are unchanged.

For each sample and state we compute the per-store change (after - before),
then:

    DiD     = mean change (NJ) - mean change (PA)
    DiD SE  = sqrt(SE_NJ^2 + SE_PA^2)

where SE is the usual standard error of the mean of the per-store changes.

Outputs:
    outputs/extension_closures.csv
    outputs/extension_closures.md

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
CSV_PATH = os.path.join(OUTPUT_DIR, "extension_closures.csv")
MD_PATH = os.path.join(OUTPUT_DIR, "extension_closures.md")

STATE_KEY = {1: "NJ", 0: "PA"}


def build_samples(records):
    """Return (baseline, excluding, n_excluded).

    baseline  -> {state_key: [per-store change, ...]} for the balanced sample.
    excluding -> same, but permanently closed stores (STATUS2 == 3) removed.
    n_excluded -> {state_key: number of permanently closed stores that were
                   actually in the balanced sample}.
    """
    baseline = {"NJ": [], "PA": []}
    excluding = {"NJ": [], "PA": []}
    n_excluded = {"NJ": 0, "PA": 0}

    for r in records:
        fb = r["fte_before"]
        fa = r["fte_after"]
        if fb is None or fa is None:
            continue
        key = STATE_KEY[r["state"]]
        change = fa - fb
        baseline[key].append(change)
        if r["status2"] == 3:
            n_excluded[key] += 1
        else:
            excluding[key].append(change)

    return baseline, excluding, n_excluded


def state_stats(changes):
    """Return (n, mean, se) for a list of per-store changes."""
    return card_common.summarize(changes)


def main():
    records = card_common.load_records()
    baseline, excluding, n_excluded = build_samples(records)

    rows = []
    for label, sample in (
        ("baseline", baseline),
        ("excluding_permanent_closures", excluding),
    ):
        n_nj, m_nj, se_nj = state_stats(sample["NJ"])
        n_pa, m_pa, se_pa = state_stats(sample["PA"])
        did = (m_nj - m_pa) if (m_nj is not None and m_pa is not None) else None
        did_se = (
            math.sqrt(se_nj ** 2 + se_pa ** 2)
            if (se_nj is not None and se_pa is not None)
            else None
        )
        rows.append({
            "label": label,
            "n_nj": n_nj, "m_nj": m_nj, "se_nj": se_nj,
            "n_pa": n_pa, "m_pa": m_pa, "se_pa": se_pa,
            "did": did, "did_se": did_se,
        })

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ---- CSV (long format) ----
    with open(CSV_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sample", "metric", "state", "n",
                    "estimate", "se"])
        for r in rows:
            w.writerow([r["label"], "change", "NJ", r["n_nj"],
                        _fmt(r["m_nj"], 6), _fmt(r["se_nj"], 6)])
            w.writerow([r["label"], "change", "PA", r["n_pa"],
                        _fmt(r["m_pa"], 6), _fmt(r["se_pa"], 6)])
            w.writerow([r["label"], "did", "NJ-PA", "",
                        _fmt(r["did"], 6), _fmt(r["did_se"], 6)])

    # ---- Markdown ----
    md = []
    md.append("# Sensitivity check: excluding permanently closed restaurants\n")
    md.append(
        "Research question: is the NJ vs. PA difference in the per-store change "
        "in full-time-equivalent employment still similar when the permanently "
        "closed restaurants are dropped?"
    )
    md.append("")
    md.append("## Sample rules\n")
    md.append(
        "- **Baseline** = the Table 3 row-4 balanced sample: FTE valid in both "
        "waves, with a permanently closed store (STATUS2 = 3) set to "
        "after-FTE = 0 and a temporarily closed store (after-FTE missing) "
        "excluded."
    )
    md.append(
        "- **Excluding permanent closures** = the baseline sample minus stores "
        "with STATUS2 = 3. All other missing-value and temporary-closure rules "
        "are unchanged."
    )
    md.append("")
    md.append("## Results\n")
    md.append("| Sample | State | N | Mean change | SE |")
    md.append("|--------|-------|---|-------------|----|")
    for r in rows:
        md.append(f"| {r['label']} | NJ | {r['n_nj']} | "
                  f"{r['m_nj']:.4f} | {r['se_nj']:.4f} |")
        md.append(f"| {r['label']} | PA | {r['n_pa']} | "
                  f"{r['m_pa']:.4f} | {r['se_pa']:.4f} |")
    md.append("")
    md.append("| Sample | DiD (NJ - PA) | DiD SE |")
    md.append("|--------|---------------|--------|")
    for r in rows:
        md.append(f"| {r['label']} | {r['did']:.4f} | {r['did_se']:.4f} |")
    md.append("")
    md.append("## Stores excluded (permanently closed, STATUS2 = 3)\n")
    md.append(
        f"- NJ: {n_excluded['NJ']} store(s) in the balanced sample were "
        f"permanently closed."
    )
    md.append(
        f"- PA: {n_excluded['PA']} store(s) in the balanced sample were "
        f"permanently closed."
    )
    md.append(
        "- The counts above are the stores actually present in the baseline "
        "sample, not an assumed count."
    )
    md.append("")
    md.append("## Limitations\n")
    md.append(
        "- Dropping permanently closed restaurants removes the employment loss "
        "caused by closure, so this is a **supplementary sensitivity check**, "
        "not a substitute for the main result."
    )
    md.append(
        "- The two estimates use overlapping samples, so they are NOT treated "
        "as independent estimates and no difference test between them is "
        "reported."
    )
    md.append(
        "- The result is reported as computed; non-significance is not "
        "interpreted as 'no effect'."
    )
    md.append("")

    with open(MD_PATH, "w") as f:
        f.write("\n".join(md))

    # ---- Terminal summary ----
    print("=== Sensitivity check: excluding permanently closed restaurants ===\n")
    for r in rows:
        print(f"[{r['label']}]")
        print(f"  NJ n={r['n_nj']}  mean={r['m_nj']:.4f}  SE={r['se_nj']:.4f}")
        print(f"  PA n={r['n_pa']}  mean={r['m_pa']:.4f}  SE={r['se_pa']:.4f}")
        print(f"  DiD={r['did']:.4f}  SE={r['did_se']:.4f}\n")
    print(f"Permanently closed stores excluded (present in baseline): "
          f"NJ={n_excluded['NJ']}, PA={n_excluded['PA']}")
    print("Wrote", CSV_PATH)
    print("Wrote", MD_PATH)


def _fmt(v, nd=6):
    return "" if v is None else f"{v:.{nd}f}"


if __name__ == "__main__":
    main()
