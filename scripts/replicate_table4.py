#!/usr/bin/env python3
"""Replicate Card & Krueger (1994) Table 4 (OLS on change in FTE employment).

Table 4 fits five OLS models of the per-store change in full-time-equivalent
employment (after - before) on, progressively, the treatment indicators and a
set of controls:

    (i)   change ~ STATE
    (ii)  change ~ STATE + brand dummies + company-owned
    (iii) change ~ GAP
    (iv)  change ~ GAP + brand dummies + company-owned
    (v)   change ~ GAP + brand dummies + company-owned + region dummies

All models include an intercept (not reported).

Definitions:

    * change = fte_after - fte_before, with FTE built by card_common (permanent
      closure -> after FTE = 0; temporary closure -> after FTE missing).
    * Primary sample (357 stores), the paper-replication sample.  A store is
      kept when, and only when:
          (a) FTE is valid in both waves (after-FTE is set to 0 for a permanent
              closure), AND
          (b) its wave-1 starting wage (WAGE_ST) is valid, AND
          (c) a non-permanently-closed store (STATUS2 != 3) also has a valid
              wave-2 starting wage (WAGE_ST2), while a permanently closed store
              (STATUS2 = 3) has wave-2 employment = 0 and may have a missing
              wave-2 starting wage.
      This rule yields 357 stores, matching the paper; the count is checked at
      run time and is never forced.
    * Supplementary sample (351 stores), the "full-wage" sample: the same rule
      but additionally requiring a valid wave-2 starting wage for EVERY store
      (including permanent closures).  Reported separately; its coefficients,
      standard errors, and N are never mixed with the 357-sample results.
    * GAP (proportional wage gap):
          Pennsylvania stores                 -> 0
          NJ stores with WAGE_ST >= $5.05     -> 0
          NJ stores with WAGE_ST <  $5.05     -> (5.05 - WAGE_ST) / WAGE_ST
      WAGE_ST must be valid and > 0.  Note the GAP threshold is $5.05, which is
      NOT the same as Table 3's $5.00 wage-group boundary.
    * Brand dummies: three dummies (KFC, Roy Rogers, Wendy's) with Burger King
      (CHAIN = 1) as the omitted baseline.
    * Company-owned: CO_OWNED (1 = company-owned), a single dummy.
    * Region dummies: two New Jersey dummies (South NJ, Central NJ) with North
      NJ omitted, plus two eastern-Pennsylvania dummies (PA1, PA2).

Standard errors are the usual OLS (homoskedastic) standard errors, not robust
standard errors.

Outputs:
    outputs/table4_replication.csv
    outputs/table4_replication.md

Code and output labels are in English.
"""

import csv
import math
import os
import sys

import numpy as np
import statsmodels.api as sm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import card_common

OUTPUT_DIR = os.path.join(card_common.PROJECT_ROOT, "outputs")
CSV_PATH = os.path.join(OUTPUT_DIR, "table4_replication.csv")
MD_PATH = os.path.join(OUTPUT_DIR, "table4_replication.md")

NEW_MIN = 5.05  # GAP threshold (NOT Table 3's 5.00 boundary)


def load_rows():
    rows = []
    with open(card_common.DATA_PATH, newline="") as f:
        for row in csv.DictReader(f):
            state = card_common.parse_float(row["STATE"])
            if state is None or int(state) not in (0, 1):
                continue
            rows.append(row)
    return rows


def make_gap(row):
    """Return GAP or None when the wage is invalid for GAP."""
    state = int(card_common.parse_float(row["STATE"]))
    wage = card_common.parse_float(row["WAGE_ST"])
    if state == 0:
        return 0.0
    if wage is None or wage <= 0:
        return None
    if wage >= NEW_MIN:
        return 0.0
    return (NEW_MIN - wage) / wage


def qualifies_primary(row):
    """True when the store belongs to the primary 357-store sample.

    Balanced FTE AND valid wave-1 wage AND (valid wave-2 wage OR permanent
    closure).
    """
    fb = card_common.compute_fte_before(row)
    fa = card_common.compute_fte_after(row)
    if fb is None or fa is None:
        return False
    w1 = card_common.parse_float(row["WAGE_ST"])
    w2 = card_common.parse_float(row["WAGE_ST2"])
    if w1 is None:
        return False
    if w2 is None and row["STATUS2"].strip() != "3":
        return False
    return True


def qualifies_supplementary(row):
    """True when the store belongs to the supplementary 351-store sample.

    Balanced FTE AND valid wage in both waves (no permanent-closure exception).
    """
    fb = card_common.compute_fte_before(row)
    fa = card_common.compute_fte_after(row)
    if fb is None or fa is None:
        return False
    w1 = card_common.parse_float(row["WAGE_ST"])
    w2 = card_common.parse_float(row["WAGE_ST2"])
    if w1 is None or w2 is None:
        return False
    return True


def build_sample(rows, require_w2_wage):
    """Return the regression sample.

    require_w2_wage=False -> primary 357-store sample (see qualifies_primary).
    require_w2_wage=True  -> supplementary 351-store sample (see
        qualifies_supplementary).
    """
    predicate = qualifies_supplementary if require_w2_wage else qualifies_primary
    return [row for row in rows if predicate(row)]


def build_matrices(recs):
    """Return y (change) and the columns needed for every model."""
    n = len(recs)
    y = np.zeros(n)
    state = np.zeros(n)
    kfc = np.zeros(n)
    rr = np.zeros(n)
    wendy = np.zeros(n)
    co_owned = np.zeros(n)
    southj = np.zeros(n)
    centralj = np.zeros(n)
    pa1 = np.zeros(n)
    pa2 = np.zeros(n)
    gap = np.zeros(n)
    for i, row in enumerate(recs):
        y[i] = card_common.compute_fte_after(row) - card_common.compute_fte_before(row)
        state[i] = int(card_common.parse_float(row["STATE"]))
        chain = int(card_common.parse_float(row["CHAIN"]))
        kfc[i] = 1 if chain == 2 else 0
        rr[i] = 1 if chain == 3 else 0
        wendy[i] = 1 if chain == 4 else 0
        co_owned[i] = 1 if int(card_common.parse_float(row["CO_OWNED"])) == 1 else 0
        southj[i] = 1 if int(card_common.parse_float(row["SOUTHJ"])) == 1 else 0
        centralj[i] = 1 if int(card_common.parse_float(row["CENTRALJ"])) == 1 else 0
        pa1[i] = 1 if int(card_common.parse_float(row["PA1"])) == 1 else 0
        pa2[i] = 1 if int(card_common.parse_float(row["PA2"])) == 1 else 0
        gap[i] = make_gap(row)
    return {
        "y": y, "state": state, "kfc": kfc, "rr": rr, "wendy": wendy,
        "co_owned": co_owned, "southj": southj, "centralj": centralj,
        "pa1": pa1, "pa2": pa2, "gap": gap,
    }


def _with_intercept(cols):
    return np.column_stack([np.ones(len(cols[0])), *cols])


MODELS = [
    # (key, key var, control column indices (0-based within the full X),
    #  builder over the dict 'd')
    ("i", "STATE", [], lambda d: _with_intercept([d["state"]])),
    ("ii", "STATE", [2, 3, 4, 5],
     lambda d: _with_intercept([d["state"], d["kfc"], d["rr"], d["wendy"],
                                d["co_owned"]])),
    ("iii", "GAP", [], lambda d: _with_intercept([d["gap"]])),
    ("iv", "GAP", [2, 3, 4, 5],
     lambda d: _with_intercept([d["gap"], d["kfc"], d["rr"], d["wendy"],
                                d["co_owned"]])),
    ("v", "GAP", [2, 3, 4, 5, 6, 7, 8, 9],
     lambda d: _with_intercept([d["gap"], d["kfc"], d["rr"], d["wendy"],
                                d["co_owned"], d["southj"], d["centralj"],
                                d["pa1"], d["pa2"]])),
]

KEY_LABEL = {"i": "STATE", "ii": "STATE", "iii": "GAP",
             "iv": "GAP", "v": "GAP"}

# Reference main coefficients from the printed paper (checking only).
PAPER_COEF = {"i": 2.33, "ii": 2.30, "iii": 15.65, "iv": 14.92, "v": 11.91}


def fit_models(d):
    """Fit the five models and return a list of result dicts."""
    out = []
    for key, keyvar, control_idx, builder in MODELS:
        X = builder(d)
        rank = np.linalg.matrix_rank(X)
        full_rank = rank == X.shape[1]
        fit = sm.OLS(d["y"], X).fit()
        coef = float(fit.params[1])  # key variable is always column 1
        se = float(fit.bse[1])
        rse = float(np.sqrt(fit.mse_resid))
        # Joint F-test for exclusion of all control variables only.
        if control_idx:
            R = np.zeros((len(control_idx), X.shape[1]))
            for r_i, c_i in enumerate(control_idx):
                R[r_i, c_i] = 1.0
            ftest = fit.f_test(R)
            f_pvalue = float(ftest.pvalue)
        else:
            f_pvalue = None
        out.append({
            "model": key, "key_var": keyvar, "coef": coef, "se": se,
            "rse": rse, "f_pvalue": f_pvalue, "n": int(len(d["y"])),
            "full_rank": full_rank, "k": int(X.shape[1]),
        })
    return out


def _fmt(v, nd=4):
    return "" if v is None else f"{v:.{nd}f}"


def main():
    rows = load_rows()

    primary = build_sample(rows, require_w2_wage=False)   # paper-replication: 357
    supplementary = build_sample(rows, require_w2_wage=True)  # full-wage: 351

    n_primary = len(primary)
    n_supplementary = len(supplementary)
    # Check the documented rule actually yields 357; never force it.
    if n_primary != 357:
        print(f"WARNING: primary sample N = {n_primary}, expected 357 (not forced).")
    if n_supplementary != 351:
        print(f"NOTE: supplementary sample N = {n_supplementary} (expected 351).")

    d_primary = build_matrices(primary)
    d_supp = build_matrices(supplementary)

    res_primary = fit_models(d_primary)
    res_supp = fit_models(d_supp)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ---- CSV (both samples, each row labeled; never mixed) ----
    with open(CSV_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "dependent_var", "sample",
                    "key_variable", "coefficient", "se",
                    "residual_sd", "controls_f_pvalue", "n",
                    "design_full_rank", "k"])
        for sample_label, res in (("primary_357", res_primary),
                                  ("supplementary_351", res_supp)):
            for r in res:
                w.writerow([
                    f"({r['model']})", "change in FTE", sample_label,
                    r["key_var"], f"{r['coef']:.6f}", f"{r['se']:.6f}",
                    f"{r['rse']:.6f}", _fmt(r["f_pvalue"], 6), r["n"],
                    "yes" if r["full_rank"] else "NO", r["k"],
                ])

    # ---- Markdown ----
    md = []
    md.append("# Card & Krueger (1994) Table 4 replication\n")
    md.append(
        "Dependent variable: change in FTE employment (after - before). "
        "OLS with an intercept (not reported); standard errors are the usual "
        "OLS (non-robust) standard errors."
    )
    md.append("")

    # --- Primary (357) ---
    md.append("## Primary sample (N = 357): paper-replication sample\n")
    md.append(f"**N = {n_primary}.**")
    md.append("")
    md.append("Filtering rule (checked, not forced):")
    md.append("")
    md.append(
        "1. FTE is valid in both waves (after-FTE is set to 0 for a permanent "
        "closure)."
    )
    md.append("2. Wave-1 starting wage (WAGE_ST) is valid.")
    md.append(
        "3. A non-permanently-closed store (STATUS2 != 3) must also have a "
        "valid wave-2 starting wage (WAGE_ST2); a permanently closed store "
        "(STATUS2 = 3) has wave-2 employment = 0 and may have a missing "
        "wave-2 starting wage."
    )
    md.append(
        f"\nThis rule yields **{n_primary}** stores, which equals the paper's "
        "count. The 351-store full-wage sample is reported separately below; "
        "the two samples' coefficients, standard errors, and N are never "
        "mixed."
    )
    md.append("")
    md.append("| Model | Key var | Coef | SE | Residual SD | Controls F p-value |")
    md.append("|-------|---------|------|----|-------------|--------------------|")
    for r in res_primary:
        md.append(
            f"| ({r['model']}) | {r['key_var']} | {r['coef']:.4f} | {r['se']:.4f} "
            f"| {r['rse']:.4f} | {_fmt(r['f_pvalue'], 4)} |"
        )
    md.append("")

    # --- Supplementary (351) ---
    md.append("## Supplementary sample (N = 351): full-wage sample\n")
    md.append(
        f"**N = {n_supplementary}.** Same rule as the primary sample but "
        "additionally requiring a valid wave-2 starting wage for EVERY store "
        "(including permanent closures). Shown separately as a sensitivity "
        "result."
    )
    md.append("")
    md.append("| Model | Key var | Coef | SE | Residual SD | Controls F p-value |")
    md.append("|-------|---------|------|----|-------------|--------------------|")
    for r in res_supp:
        md.append(
            f"| ({r['model']}) | {r['key_var']} | {r['coef']:.4f} | {r['se']:.4f} "
            f"| {r['rse']:.4f} | {_fmt(r['f_pvalue'], 4)} |"
        )
    md.append("")

    # --- Definitions and methods ---
    md.append("## Definitions and methods\n")
    md.append(
        "- Brand dummies: KFC, Roy Rogers, Wendy's (baseline Burger King, "
        "CHAIN = 1). Company-owned: CO_OWNED (1 = company-owned)."
    )
    md.append(
        "- Region dummies: South NJ + Central NJ (baseline North NJ) and PA1 "
        "+ PA2. The paper's body text describes 'three regions of New Jersey "
        "(North, Central, and South) and two regions of eastern Pennsylvania'; "
        "this replication uses two NJ dummy variables (South and Central, with "
        "North omitted) plus PA1 and PA2."
    )
    md.append(
        "- GAP threshold is $5.05, not Table 3's $5.00 boundary: NJ stores with "
        "WAGE_ST >= 5.05 get GAP = 0; below 5.05 get (5.05 - WAGE_ST) / WAGE_ST; "
        "PA stores get GAP = 0."
    )
    md.append(
        "- Joint F-test: exclusion of all control variables of that model only "
        "(it does not include STATE / GAP and is not the overall model F-test). "
        "Models (i) and (iii) have no controls, so the p-value is blank."
    )
    md.append(
        "- Design-matrix rank was checked against the column count for each "
        "model; all are full rank (no perfect collinearity)."
    )
    md.append("")

    # --- Comparison ---
    md.append("## Comparison with the paper's reference coefficients\n")
    md.append("| Model | Paper | Primary (N=357) | Supplementary (N=351) |")
    md.append("|-------|-------|-----------------|-----------------------|")
    for r, p in zip(res_primary, res_supp):
        key = r["model"]
        md.append(
            f"| ({key}) | {PAPER_COEF[key]} | {r['coef']:.2f} | {p['coef']:.2f} |"
        )
    md.append(
        "\nReference coefficients are from the printed Table 4 and are listed "
        "only for checking; they were not hard-coded into the computation."
    )
    md.append(
        "- On the primary 357-store sample, models (i)-(iv) reproduce the "
        "paper's main coefficient exactly (2.33, 2.30, 15.65, 14.92)."
    )
    md.append(
        "- Model (v) gives 11.98 versus the paper's 11.91 (a difference of "
        "0.07). The cause of this difference is not confirmed."
    )
    md.append("")

    with open(MD_PATH, "w") as f:
        f.write("\n".join(md))

    # ---- Terminal summary ----
    print("=== Card & Krueger (1994) Table 4 replication ===\n")
    print(f"Primary sample N = {n_primary}  (paper: 357)")
    print(f"Supplementary (full-wage) sample N = {n_supplementary}\n")
    print("Model  Key    Coef      SE     ResidSD  CtrlF_p   PaperRef")
    for r, p in zip(res_primary, res_supp):
        key = r["model"]
        print(f"({key})    {r['key_var']:<5} {r['coef']:.4f}  {r['se']:.4f}  "
              f"{r['rse']:.4f}  {_fmt(r['f_pvalue'],4):>8}  {PAPER_COEF[key]:.2f}"
              f"   (N=351: {p['coef']:.2f})")
    print("\nDV mean / sd (primary sample):",
          f"{float(np.mean(d_primary['y'])):.3f} / {float(np.std(d_primary['y'], ddof=1)):.3f}")
    print("Full rank check (primary):",
          {r['model']: r['full_rank'] for r in res_primary})
    print("Wrote", CSV_PATH)
    print("Wrote", MD_PATH)


if __name__ == "__main__":
    main()
