# Card & Krueger (1994) Table 4 replication

Dependent variable: change in FTE employment (after - before). OLS with an intercept (not reported); standard errors are the usual OLS (non-robust) standard errors.

## Primary sample (N = 357): paper-replication sample

**N = 357.**

Filtering rule (checked, not forced):

1. FTE is valid in both waves (after-FTE is set to 0 for a permanent closure).
2. Wave-1 starting wage (WAGE_ST) is valid.
3. A non-permanently-closed store (STATUS2 != 3) must also have a valid wave-2 starting wage (WAGE_ST2); a permanently closed store (STATUS2 = 3) has wave-2 employment = 0 and may have a missing wave-2 starting wage.

This rule yields **357** stores, which equals the paper's count. The 351-store full-wage sample is reported separately below; the two samples' coefficients, standard errors, and N are never mixed.

| Model | Key var | Coef | SE | Residual SD | Controls F p-value |
|-------|---------|------|----|-------------|--------------------|
| (i) | STATE | 2.3258 | 1.1916 | 8.7909 |  |
| (ii) | STATE | 2.3039 | 1.1955 | 8.7847 | 0.3443 |
| (iii) | GAP | 15.6529 | 6.0802 | 8.7565 |  |
| (iv) | GAP | 14.9157 | 6.2053 | 8.7592 | 0.4374 |
| (v) | GAP | 11.9792 | 7.4191 | 8.7525 | 0.4046 |

## Supplementary sample (N = 351): full-wage sample

**N = 351.** Same rule as the primary sample but additionally requiring a valid wave-2 starting wage for EVERY store (including permanent closures). Shown separately as a sensitivity result.

| Model | Key var | Coef | SE | Residual SD | Controls F p-value |
|-------|---------|------|----|-------------|--------------------|
| (i) | STATE | 2.2769 | 1.1904 | 8.7146 |  |
| (ii) | STATE | 2.2815 | 1.1970 | 8.7205 | 0.4752 |
| (iii) | GAP | 17.0516 | 6.0901 | 8.6634 |  |
| (iv) | GAP | 16.3631 | 6.2373 | 8.6802 | 0.6181 |
| (v) | GAP | 13.8790 | 7.4440 | 8.6695 | 0.4846 |

## Definitions and methods

- Brand dummies: KFC, Roy Rogers, Wendy's (baseline Burger King, CHAIN = 1). Company-owned: CO_OWNED (1 = company-owned).
- Region dummies: South NJ + Central NJ (baseline North NJ) and PA1 + PA2. The paper's body text describes 'three regions of New Jersey (North, Central, and South) and two regions of eastern Pennsylvania'; this replication uses two NJ dummy variables (South and Central, with North omitted) plus PA1 and PA2.
- GAP threshold is $5.05, not Table 3's $5.00 boundary: NJ stores with WAGE_ST >= 5.05 get GAP = 0; below 5.05 get (5.05 - WAGE_ST) / WAGE_ST; PA stores get GAP = 0.
- Joint F-test: exclusion of all control variables of that model only (it does not include STATE / GAP and is not the overall model F-test). Models (i) and (iii) have no controls, so the p-value is blank.
- Design-matrix rank was checked against the column count for each model; all are full rank (no perfect collinearity).

## Comparison with the paper's reference coefficients

| Model | Paper | Primary (N=357) | Supplementary (N=351) |
|-------|-------|-----------------|-----------------------|
| (i) | 2.33 | 2.33 | 2.28 |
| (ii) | 2.3 | 2.30 | 2.28 |
| (iii) | 15.65 | 15.65 | 17.05 |
| (iv) | 14.92 | 14.92 | 16.36 |
| (v) | 11.91 | 11.98 | 13.88 |

Reference coefficients are from the printed Table 4 and are listed only for checking; they were not hard-coded into the computation.
- On the primary 357-store sample, models (i)-(iv) reproduce the paper's main coefficient exactly (2.33, 2.30, 15.65, 14.92).
- Model (v) gives 11.98 versus the paper's 11.91 (a difference of 0.07). The cause of this difference is not confirmed.
