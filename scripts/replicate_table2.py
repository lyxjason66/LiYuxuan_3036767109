#!/usr/bin/env python3
"""Replicate Card & Krueger (1994) Table 2 (full table).

Table 2 reports, for New Jersey and Pennsylvania, the distribution of store
types and the wave-1 / wave-2 means (or percentages) of a set of store-level
characteristics, together with a two-state test of equality.

Sections of the original table:

    1. Distribution of store types (percentages):
         Burger King, KFC, Roy Rogers, Wendy's, company-owned.
    2. Means in wave 1:
         FTE employment, % full-time employees, starting wage,
         wage = $4.25 (%), price of full meal, hours open, recruiting bonus (%).
    3. Means in wave 2:
         FTE employment, % full-time employees, starting wage,
         wage = $4.25 (%), wage = $5.05 (%), price of full meal, hours open,
         recruiting bonus (%).

Definitions / rules (this replication):

    * FTE (before) = EMPFT + NMGRS + 0.5 * EMPPT; FTE (after) likewise with
      the "2"-suffix variables.  A missing component leaves FTE missing.
      Permanent closures (STATUS2 = 3) have after FTE = 0; temporary closures
      (STATUS2 in {2, 4, 5}) have after FTE missing (shared via card_common).
    * Price of a full meal = PSODA + PFRY + PENTREE (wave 1) or
      PSODA2 + PFRY2 + PENTREE2 (wave 2); missing if any component is missing.
    * Hours open = HRSOPEN (wave 1) / HRSOPEN2 (wave 2).
    * Recruiting bonus = BONUS (wave 1); SPECIAL2 (wave 2).  SPECIAL2 is the
      wave-2 field: it reproduces the paper's wave-2 recruiting-bonus shares
      exactly (NJ 20.3, PA 23.4), so it is treated as the wave-2 bonus field
      rather than inferred from its generic label.
    * "wage = X" indicators are 1 when the starting wage equals X exactly
      (compared on integer cents).  Two denominators are computed side by side:
          (a) "all stores"  -- a missing wage is treated as "not equal to X",
              so the denominator is every store in the state (this is the
              paper's apparent comparison basis);
          (b) "valid wage"  -- a missing wage is excluded, so the denominator
              is the number of valid wage records in that state-period.
      Each denominator gets its own SE and its own two-state t; the two are
      never mixed.
    * Each metric uses its own valid sample: rows with a missing value for
      that metric are dropped for that metric only (no unified row deletion).

Standard errors:

    * Continuous variable: SEM = sample sd / sqrt(n).
    * Percentage (0/1 indicator): SE = sqrt(p * (1 - p) / n) * 100.
    * Two-state comparison: t = (m_NJ - m_PA) / sqrt(se_NJ^2 + se_PA^2),
      i.e. a two-sample test of equality of means with independent,
      unequal-variance states (Welch); for percentages this is the unpooled
      two-sample proportion test.

Outputs:
    outputs/table2_replication.csv
    outputs/table2_sample_counts.csv
    outputs/table2_replication.md

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
CSV_PATH = os.path.join(OUTPUT_DIR, "table2_replication.csv")
COUNTS_PATH = os.path.join(OUTPUT_DIR, "table2_sample_counts.csv")
MD_PATH = os.path.join(OUTPUT_DIR, "table2_replication.md")


def load_rows():
    """Return raw record dicts for STATE in {0, 1}."""
    rows = []
    with open(card_common.DATA_PATH, newline="") as f:
        for row in csv.DictReader(f):
            state = card_common.parse_float(row["STATE"])
            if state is None or int(state) not in (0, 1):
                continue
            rows.append(row)
    return rows


def _meal(row, suffix=""):
    """Price of a full meal; missing if any component is missing."""
    vals = [card_common.parse_float(row[k + suffix])
            for k in ("PSODA", "PFRY", "PENTREE")]
    if any(v is None for v in vals):
        return None
    return sum(vals)


def _pct_fulltime_incl(row, suffix=""):
    """% full-time including managers: (E + M) / (E + M + P) * 100."""
    e = card_common.parse_float(row["EMPFT" + suffix])
    p = card_common.parse_float(row["EMPPT" + suffix])
    m = card_common.parse_float(row["NMGRS" + suffix])
    if e is None or p is None or m is None:
        return None
    total = e + m + p
    return 100.0 * (e + m) / total if total > 0 else None


def _pct_fulltime_excl(row, suffix=""):
    """% full-time excluding managers: E / (E + P) * 100."""
    e = card_common.parse_float(row["EMPFT" + suffix])
    p = card_common.parse_float(row["EMPPT" + suffix])
    if e is None or p is None:
        return None
    total = e + p
    return 100.0 * e / total if total > 0 else None


def _wage_eq(col):
    """Return a callable row -> {1, 0, None} for 'wage equals X'.

    A missing wage stays missing (excluded from the valid-wage denominator).
    """

    def fn(row, target):
        w = card_common.parse_float(row[col])
        if w is None:
            return None  # missing wage stays missing, not False
        return 1 if round(w * 100) == round(target * 100) else 0

    return fn


def _wage_eq_all(col):
    """Return a callable row -> {1, 0} for 'wage equals X' (all-stores rule).

    A missing wage is treated as 'not equal to X' (0), so the denominator is
    every store in the state rather than every valid wage record.
    """

    def fn(row, target):
        w = card_common.parse_float(row[col])
        if w is None:
            return 0  # missing -> "not equal to X" (all-stores denominator)
        return 1 if round(w * 100) == round(target * 100) else 0

    return fn


# Wage == X rows, mapped to their data column and target value, for the
# dual-denominator computation.  (section, key) -> (column, target).
WAGE_EQ = {
    (2, "wage_425"): ("WAGE_ST", 4.25),
    (3, "wage_425"): ("WAGE_ST2", 4.25),
    (3, "wage_505"): ("WAGE_ST2", 5.05),
}


# ---------------------------------------------------------------------------
# Metric specification.
#
# Each spec is (section, key, label, kind, extractor).
#   kind "mean"  -> continuous variable, SEM reported.
#   kind "prop"  -> 0/1 indicator, percentage with proportion SE.
# extractor(row) -> float value or None (missing); for "prop" it returns 0/1.
# ---------------------------------------------------------------------------
def _specs():
    specs = []
    sec1 = [
        ("bk", "Burger King", lambda r: _ind(r, "CHAIN", 1)),
        ("kfc", "KFC", lambda r: _ind(r, "CHAIN", 2)),
        ("rr", "Roy Rogers", lambda r: _ind(r, "CHAIN", 3)),
        ("wendy", "Wendy's", lambda r: _ind(r, "CHAIN", 4)),
        ("co_owned", "Company-owned", lambda r: _ind(r, "CO_OWNED", 1)),
    ]
    for key, label, fn in sec1:
        specs.append((1, key, label, "prop", fn))

    sec2 = [
        ("fte", "FTE employment", "mean",
         lambda r: card_common.compute_fte_before(r)),
        ("pct_ft", "% full-time employees (incl. managers)", "mean",
         lambda r: _pct_fulltime_incl(r, "")),
        ("wage", "Starting wage", "mean",
         lambda r: card_common.parse_float(r["WAGE_ST"])),
        ("wage_425", "Wage = $4.25 (%)", "prop",
         _wage_eq("WAGE_ST")),
        ("meal", "Price of full meal", "mean",
         lambda r: _meal(r, "")),
        ("hours", "Hours open (weekday)", "mean",
         lambda r: card_common.parse_float(r["HRSOPEN"])),
        ("bonus", "Recruiting bonus (%)", "prop",
         lambda r: _ind(r, "BONUS", 1)),
    ]
    for key, label, kind, fn in sec2:
        specs.append((2, key, label, kind, fn))

    sec3 = [
        ("fte", "FTE employment", "mean",
         lambda r: card_common.compute_fte_after(r)),
        ("pct_ft", "% full-time employees (incl. managers)", "mean",
         lambda r: _pct_fulltime_incl(r, "2")),
        ("wage", "Starting wage", "mean",
         lambda r: card_common.parse_float(r["WAGE_ST2"])),
        ("wage_425", "Wage = $4.25 (%)", "prop",
         _wage_eq("WAGE_ST2")),
        ("wage_505", "Wage = $5.05 (%)", "prop",
         _wage_eq("WAGE_ST2")),
        ("meal", "Price of full meal", "mean",
         lambda r: _meal(r, "2")),
        ("hours", "Hours open (weekday)", "mean",
         lambda r: card_common.parse_float(r["HRSOPEN2"])),
        ("bonus", "Recruiting bonus (%)", "prop",
         lambda r: _ind(r, "SPECIAL2", 1)),
    ]
    for key, label, kind, fn in sec3:
        specs.append((3, key, label, kind, fn))

    return specs


def _ind(row, col, val):
    """Return 0/1 for row[col] == val, None if the column is missing."""
    v = card_common.parse_float(row[col])
    if v is None:
        return None
    return 1 if v == val else 0


# Reference values from the printed paper, for checking only (never used to
# compute or force a result).
PAPER_REF = {
    (1, "bk"): (41.1, 44.3, None),
    (1, "kfc"): (20.5, 15.2, None),
    (1, "rr"): (24.8, 21.5, None),
    (1, "wendy"): (13.6, 19.0, None),
    (1, "co_owned"): (34.1, 35.4, None),
    (2, "fte"): (20.4, 23.3, -2.0),
    (2, "pct_ft"): (32.8, 35.9, -1.0),
    (2, "wage"): (4.61, 4.63, -0.4),
    (2, "wage_425"): (30.5, 32.9, -0.4),
    (2, "meal"): (3.35, 3.04, 3.9),
    (2, "hours"): (14.4, 14.5, -0.3),
    (2, "bonus"): (23.6, 29.1, -1.0),
    (3, "fte"): (21.0, 21.2, -0.2),
    (3, "pct_ft"): (35.9, 30.4, 1.8),
    (3, "wage"): (5.08, 4.62, 10.8),
    (3, "wage_425"): (0.0, 25.3, None),
    (3, "wage_505"): (85.2, 1.3, 36.1),
    (3, "meal"): (3.41, 3.03, 5.0),
    (3, "hours"): (14.4, 14.7, -0.8),
    (3, "bonus"): (20.3, 23.4, -0.6),
}


def summarize_mean(values):
    """Return (n, mean, sem) for a continuous variable."""
    return card_common.summarize(values)


def summarize_prop(values):
    """Return (n, pct, se_pct) for a 0/1 indicator (SE = sqrt(p(1-p)/n))."""
    n = len(values)
    if n == 0:
        return 0, None, None
    p = sum(values) / n
    pct = 100.0 * p
    if n < 2:
        return n, pct, None
    se_pct = 100.0 * math.sqrt(p * (1.0 - p) / n)
    return n, pct, se_pct


def t_stat(m_nj, se_nj, m_pa, se_pa):
    """Two-state test of equality: (m_NJ - m_PA) / sqrt(se_NJ^2 + se_PA^2)."""
    if m_nj is None or m_pa is None:
        return None
    if se_nj is None or se_pa is None:
        return None
    denom = math.sqrt(se_nj ** 2 + se_pa ** 2)
    if denom == 0:
        return None
    return (m_nj - m_pa) / denom


def _fmt(value, nd=2):
    return "" if value is None else f"{value:.{nd}f}"


def main():
    rows = load_rows()
    specs = _specs()

    # Partition records by state once.
    by_state = {0: [r for r in rows if int(card_common.parse_float(r["STATE"])) == 0],
                1: [r for r in rows if int(card_common.parse_float(r["STATE"])) == 1]}

    results = []  # dicts, one per (section, key)
    for section, key, label, kind, extractor in specs:
        # The "wage = X" extractors are parameterized by a target; resolve it.
        if key in ("wage_425", "wage_505"):
            target = 4.25 if key == "wage_425" else 5.05
            fn = lambda r, _t=target, _e=extractor: _e(r, _t)
        else:
            fn = extractor

        nj_vals = [v for v in (fn(r) for r in by_state[1]) if v is not None]
        pa_vals = [v for v in (fn(r) for r in by_state[0]) if v is not None]

        if kind == "mean":
            n_nj, m_nj, se_nj = summarize_mean(nj_vals)
            n_pa, m_pa, se_pa = summarize_mean(pa_vals)
        else:
            n_nj, m_nj, se_nj = summarize_prop(nj_vals)
            n_pa, m_pa, se_pa = summarize_prop(pa_vals)

        t = t_stat(m_nj, se_nj, m_pa, se_pa)
        results.append({
            "section": section,
            "key": key,
            "label": label,
            "kind": kind,
            "n_nj": n_nj, "m_nj": m_nj, "se_nj": se_nj,
            "n_pa": n_pa, "m_pa": m_pa, "se_pa": se_pa,
            "t": t,
        })

    # Wage == X under the "all stores in the state" denominator: a missing wage
    # is treated as "not equal to X" (0), so the denominator is every store in
    # the state.  Keyed by (section, key).
    wage_all = {}
    for (section, key), (col, target) in WAGE_EQ.items():
        fn = _wage_eq_all(col)
        nj_vals = [fn(r, target) for r in by_state[1]]
        pa_vals = [fn(r, target) for r in by_state[0]]
        n_nj, m_nj, se_nj = summarize_prop(nj_vals)
        n_pa, m_pa, se_pa = summarize_prop(pa_vals)
        wage_all[(section, key)] = {
            "n_nj": n_nj, "m_nj": m_nj, "se_nj": se_nj,
            "n_pa": n_pa, "m_pa": m_pa, "se_pa": se_pa,
            "t": t_stat(m_nj, se_nj, m_pa, se_pa),
        }

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ---- CSV (wide, one row per item; wage=X items get both denominators) ----
    with open(CSV_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["section", "item", "denominator", "kind",
                    "nj_estimate", "nj_se", "nj_n",
                    "pa_estimate", "pa_se", "pa_n",
                    "t_nj_pa"])
        for r in results:
            if (r["section"], r["key"]) in WAGE_EQ:
                # valid-wage denominator (descriptive: missing excluded)
                w.writerow([
                    r["section"], r["key"], "valid_wage", r["kind"],
                    _fmt(r["m_nj"], 4), _fmt(r["se_nj"], 4), r["n_nj"],
                    _fmt(r["m_pa"], 4), _fmt(r["se_pa"], 4), r["n_pa"],
                    _fmt(r["t"], 4),
                ])
                # all-stores denominator (paper-style: missing -> not equal)
                wa = wage_all[(r["section"], r["key"])]
                w.writerow([
                    r["section"], r["key"], "all_stores", r["kind"],
                    _fmt(wa["m_nj"], 4), _fmt(wa["se_nj"], 4), wa["n_nj"],
                    _fmt(wa["m_pa"], 4), _fmt(wa["se_pa"], 4), wa["n_pa"],
                    _fmt(wa["t"], 4),
                ])
            else:
                w.writerow([
                    r["section"], r["key"], "", r["kind"],
                    _fmt(r["m_nj"], 4), _fmt(r["se_nj"], 4), r["n_nj"],
                    _fmt(r["m_pa"], 4), _fmt(r["se_pa"], 4), r["n_pa"],
                    _fmt(r["t"], 4),
                ])

    # ---- Sample-count CSV ----
    with open(COUNTS_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["section", "item", "denominator", "n_nj", "n_pa"])
        for r in results:
            if (r["section"], r["key"]) in WAGE_EQ:
                wa = wage_all[(r["section"], r["key"])]
                w.writerow([r["section"], r["key"], "valid_wage", r["n_nj"], r["n_pa"]])
                w.writerow([r["section"], r["key"], "all_stores", wa["n_nj"], wa["n_pa"]])
            else:
                w.writerow([r["section"], r["key"], "", r["n_nj"], r["n_pa"]])

    # ---- Markdown ----
    md = []
    md.append("# Card & Krueger (1994) Table 2 replication\n")
    md.append(
        "Estimates are the replication's computed values (SE in parentheses); "
        "`t` is the two-state test of equality of means. `Paper` lists the "
        "printed values for checking only."
    )
    md.append("")
    section_titles = {1: "1. Distribution of store types (percentages)",
                      2: "2. Means in wave 1",
                      3: "3. Means in wave 2"}
    for section in (1, 2, 3):
        md.append(f"## {section_titles[section]}\n")
        md.append("| Item | NJ | PA | t | Paper NJ | Paper PA | Paper t |")
        md.append("|------|----|----|---|----------|----------|---------|")
        for r in results:
            if r["section"] != section:
                continue
            if (section, r["key"]) in WAGE_EQ:
                # Display the all-stores denominator (the paper's comparison
                # basis); the valid-wage denominator is in the diagnostic
                # section below.
                wa = wage_all[(section, r["key"])]
                nj = f"{wa['m_nj']:.2f} ({_fmt(wa['se_nj'], 2)})"
                pa = f"{wa['m_pa']:.2f} ({_fmt(wa['se_pa'], 2)})"
                t = _fmt(wa["t"], 1)
                label = r["label"].replace("(%)", "(%, all stores)")
            else:
                nj = f"{r['m_nj']:.2f} ({_fmt(r['se_nj'], 2)})" if r["m_nj"] is not None else ""
                pa = f"{r['m_pa']:.2f} ({_fmt(r['se_pa'], 2)})" if r["m_pa"] is not None else ""
                t = _fmt(r["t"], 1)
                label = r["label"]
            pref = PAPER_REF.get((section, r["key"]))
            pnj = _fmt(pref[0], 2) if pref else ""
            ppa = _fmt(pref[1], 2) if pref else ""
            pt = _fmt(pref[2], 1) if pref else ""
            md.append(f"| {label} | {nj} | {pa} | {t} | {pnj} | {ppa} | {pt} |")
        md.append("")

    md.append("## Definitions and methods\n")
    md.append(
        "- FTE (before) = EMPFT + NMGRS + 0.5 * EMPPT; FTE (after) uses the "
        "'2'-suffix variables. Permanent closure (STATUS2 = 3) -> after FTE = 0; "
        "temporary closure (STATUS2 in {2, 4, 5}) -> after FTE missing."
    )
    md.append(
        "- Full meal price = PSODA + PFRY + PENTREE (wave 2: PSODA2 + PFRY2 + "
        "PENTREE2); missing if any component is missing."
    )
    md.append(
        "- Recruiting bonus = BONUS (wave 1) and SPECIAL2 (wave 2). SPECIAL2 "
        "reproduces the paper's wave-2 bonus shares exactly (NJ 20.3, PA 23.4), "
        "so it is taken as the wave-2 bonus field (not assumed from its label)."
    )
    md.append(
        "- `% full-time employees`: computed including managers as "
        "(EMPFT + NMGRS) / (EMPFT + NMGRS + EMPPT), consistent with the paper's "
        "FTE note that 'full-time workers' includes managers. This is the value "
        "shown above; it does NOT match the paper's printed 32.8 / 35.9 / 30.4, "
        "so the paper's exact % full-time definition is UNCONFIRMED. The "
        "managers-excluded variant (EMPFT / (EMPFT + EMPPT)) is reported in a "
        "separate diagnostic table below; it also does not match."
    )
    md.append(
        "- Each metric uses its own valid sample; no unified row deletion."
    )
    md.append("")
    md.append("## Standard errors and t-test\n")
    md.append(
        "- Continuous variable: SEM = sample sd / sqrt(n)."
    )
    md.append(
        "- Percentage: SE = sqrt(p (1 - p) / n) * 100."
    )
    md.append(
        "- Two-state comparison: t = (m_NJ - m_PA) / sqrt(se_NJ^2 + se_PA^2), "
        "a two-sample test of equality of means (independent states, unequal "
        "variance / unpooled proportions)."
    )
    md.append("")
    md.append("## Known differences from the paper\n")
    md.append(
        "- **`wage = X` denominators.** For 'wage = $4.25' and 'wage = $5.05' "
        "two denominators are reported -- every store in the state (missing "
        "wage treated as 'not equal to X') and valid wage records only (missing "
        "excluded) -- see the diagnostic section below. The all-stores "
        "denominator is the one that matches the paper's printed percentages, "
        "except NJ wave-2 'wage = $5.05' (see below). The original raw missing "
        "values are not modified, and the authors' original code is not "
        "claimed to have been verified."
    )
    md.append(
        "- **% full-time employees.** Definition unconfirmed (see above); the "
        "computed values differ from the paper's, so this row is NOT treated "
        "as replicated."
    )
    md.append(
        "- Store-type rows are reported without standard errors or t-tests in "
        "the paper; this replication computes them for completeness, and the "
        "proportions match the printed values exactly."
    )
    md.append("")

    # Diagnostic: wage = X under two denominators (all stores vs valid wage).
    res_by_key = {(r["section"], r["key"]): r for r in results}
    md.append("## Diagnostic: `wage = X` under two denominators\n")
    md.append(
        "For each 'wage = X' cell the numerator (count == X), the two "
        "denominators (all stores in the state vs. valid wage records), the "
        "number of missing wages, the percentage (SE), and the two-state t are "
        "shown. 'Match' compares the rounded percentage to the paper's printed "
        "value. The numerator is identical for the two denominators (a missing "
        "wage can never equal X); only the denominator differs."
    )
    md.append("")
    for (section, key) in WAGE_EQ:
        col, target = WAGE_EQ[(section, key)]
        wave = "1" if section == 2 else "2"
        r = res_by_key[(section, key)]
        wa = wage_all[(section, key)]
        fn_all = _wage_eq_all(col)
        num_nj = sum(fn_all(x, target) for x in by_state[1])
        num_pa = sum(fn_all(x, target) for x in by_state[0])
        missing_nj = sum(1 for x in by_state[1] if card_common.parse_float(x[col]) is None)
        missing_pa = sum(1 for x in by_state[0] if card_common.parse_float(x[col]) is None)
        pref = PAPER_REF[(section, key)]
        paper_nj, paper_pa, paper_t = pref
        md.append(f"**Wave {wave} -- {r['label']} (target = {target:.2f})**\n")
        md.append("| State | Denominator | count == X | N (denom) | missing | % (SE) |")
        md.append("|---|---|---|---|---|---|")
        md.append(f"| NJ | all stores | {num_nj} | {wa['n_nj']} | {missing_nj} | "
                  f"{wa['m_nj']:.2f} ({_fmt(wa['se_nj'], 2)}) |")
        md.append(f"| NJ | valid wage | {num_nj} | {r['n_nj']} | {missing_nj} | "
                  f"{r['m_nj']:.2f} ({_fmt(r['se_nj'], 2)}) |")
        md.append(f"| PA | all stores | {num_pa} | {wa['n_pa']} | {missing_pa} | "
                  f"{wa['m_pa']:.2f} ({_fmt(wa['se_pa'], 2)}) |")
        md.append(f"| PA | valid wage | {num_pa} | {r['n_pa']} | {missing_pa} | "
                  f"{r['m_pa']:.2f} ({_fmt(r['se_pa'], 2)}) |")
        md.append("")
        paper_t_txt = (f"paper t = {_fmt(paper_t, 1)}" if paper_t is not None
                       else "paper t not reported")
        md.append(
            f"t (NJ-PA): all stores = {_fmt(wa['t'], 1)}, valid wage = "
            f"{_fmt(r['t'], 1)}; {paper_t_txt}. "
            f"Paper: NJ {paper_nj:.1f}, PA {paper_pa:.1f}. "
            f"Match (all stores): NJ {'yes' if abs(wa['m_nj'] - paper_nj) < 0.05 else 'no'}, "
            f"PA {'yes' if abs(wa['m_pa'] - paper_pa) < 0.05 else 'no'}; "
            f"match (valid wage): NJ {'yes' if abs(r['m_nj'] - paper_nj) < 0.05 else 'no'}, "
            f"PA {'yes' if abs(r['m_pa'] - paper_pa) < 0.05 else 'no'}."
        )
        md.append("")
    md.append(
        "- **NJ wave-2 'wage = $5.05'.** The all-stores denominator gives "
        "85.50% (283 / 331), while the paper prints 85.2% (equal to 282 / 331). "
        "The public data contain 283 NJ wave-2 records at exactly $5.05; one of "
        "them (sheet 65) is a temporarily closed store (STATUS2 = 2). Whether "
        "the paper excludes that store is unconfirmed; the raw value is left "
        "unchanged."
    )
    md.append("")

    # Diagnostic: % full-time excluding managers (both waves).
    md.append("## Diagnostic: % full-time excluding managers\n")
    md.append(
        "For checking the unconfirmed definition, the managers-excluded "
        "variant (EMPFT / (EMPFT + EMPPT)) is:\n"
    )
    md.append("| Wave | NJ mean | NJ n | PA mean | PA n |")
    md.append("|------|---------|------|---------|------|")
    for suffix, wave in (("", "1"), ("2", "2")):
        nj_vals = [v for v in (_pct_fulltime_excl(r, suffix) for r in by_state[1])
                   if v is not None]
        pa_vals = [v for v in (_pct_fulltime_excl(r, suffix) for r in by_state[0])
                   if v is not None]
        n_nj, m_nj, _ = summarize_mean(nj_vals)
        n_pa, m_pa, _ = summarize_mean(pa_vals)
        md.append(f"| {wave} | {m_nj:.2f} | {n_nj} | {m_pa:.2f} | {n_pa} |")
    md.append("")

    with open(MD_PATH, "w") as f:
        f.write("\n".join(md))

    # ---- Terminal summary ----
    print("=== Card & Krueger (1994) Table 2 replication ===\n")
    for section in (1, 2, 3):
        print(f"[{section_titles[section]}]")
        for r in results:
            if r["section"] != section:
                continue
            nj = (f"{r['m_nj']:.2f} (SE {_fmt(r['se_nj'],2)}, n={r['n_nj']})"
                  if r["m_nj"] is not None else "NA")
            pa = (f"{r['m_pa']:.2f} (SE {_fmt(r['se_pa'],2)}, n={r['n_pa']})"
                  if r["m_pa"] is not None else "NA")
            t = _fmt(r["t"], 2)
            print(f"  {r['label']:<40} NJ {nj:<28} PA {pa:<28} t={t}")
        print()
    print("Wrote", CSV_PATH)
    print("Wrote", COUNTS_PATH)
    print("Wrote", MD_PATH)


if __name__ == "__main__":
    main()
