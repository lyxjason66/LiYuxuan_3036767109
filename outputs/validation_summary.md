# Baseline replication — validation summary

Computed results vs. the printed Card & Krueger (1994) paper. Everything below
is a **computed result** unless marked otherwise; nothing was forced to match,
and the authors' original code is not claimed to have been verified.

## Main sample (Table 4)

- **Primary sample N = 357** (matches the paper's count). Rule: FTE valid in
  both waves AND wave-1 starting wage valid; a non-permanently-closed store
  (STATUS2 != 3) must also have a valid wave-2 wage, while a permanently closed
  store (STATUS2 = 3) has wave-2 employment = 0 and may have a missing wave-2
  wage. Checked at run time, not forced.
- **Supplementary sample N = 351** (full-wage sensitivity result, same rule
  plus a valid wave-2 wage for every store). Reported separately.

## Matched (computed)

- **Table 2 store types** — all five proportions match the paper exactly
  (BK 41.1 / 44.3, KFC 20.5 / 15.2, Roy Rogers 24.8 / 21.5, Wendy's 13.6 /
  19.0, company-owned 34.1 / 35.4).
- **Table 2 wave-1 and wave-2 means** — FTE employment, starting wage, price of
  a full meal, hours open, and recruiting bonus match the paper (within the
  reported rounding).
- **Table 2 `wage = X`, all-stores denominator** — matches the paper for
  wave-1 wage = $4.25 (NJ 30.5, PA 32.9, t = -0.4), wave-2 wage = $4.25
  (NJ 0.0, PA 25.3), and PA wave-2 wage = $5.05 (1.3).
- **Table 4 models (i)-(iv) on the primary 357 sample** — reproduce the
  paper's coefficients exactly (2.33, 2.30, 15.65, 14.92).

## Remaining differences (computed; cause not confirmed)

- **Table 2 NJ wave-2 `wage = $5.05`** — 85.50% (283 / 331) vs. the paper's
  85.2% (= 282 / 331). The public data contain 283 NJ wave-2 records at exactly
  $5.05; one of them is a temporarily closed store (STATUS2 = 2). Cause not
  confirmed; the raw value is left unchanged.
- **Table 4 model (v)** — 11.98 vs. the paper's 11.91 (difference 0.07). Cause
  not confirmed.

## Unconfirmed definitions (not replicated)

- **Table 2 `% full-time employees`** — definition unconfirmed. Neither the
  managers-included nor managers-excluded formula reproduces the paper's
  32.8 / 35.9 / 30.4.
- **Table 3 row-3 standard errors** — not yet reproduced (the original SE
  formula is unconfirmed).
- **Figure 1 bin boundaries** — the original rule is not stated in the scan;
  the 10-cent bins are a documented replication choice (see figure1_notes.md).

## Speculation

Earlier unevidenced explanations were removed: "the paper used rounded means to
compute t" and "model (v) differs because of region coding". Both are now
recorded as **cause not confirmed** (no directly citable evidence was found).
