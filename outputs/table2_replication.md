# Card & Krueger (1994) Table 2 replication

Estimates are the replication's computed values (SE in parentheses); `t` is the two-state test of equality of means. `Paper` lists the printed values for checking only.

## 1. Distribution of store types (percentages)

| Item | NJ | PA | t | Paper NJ | Paper PA | Paper t |
|------|----|----|---|----------|----------|---------|
| Burger King | 41.09 (2.70) | 44.30 (5.59) | -0.5 | 41.10 | 44.30 |  |
| KFC | 20.54 (2.22) | 15.19 (4.04) | 1.2 | 20.50 | 15.20 |  |
| Roy Rogers | 24.77 (2.37) | 21.52 (4.62) | 0.6 | 24.80 | 21.50 |  |
| Wendy's | 13.60 (1.88) | 18.99 (4.41) | -1.1 | 13.60 | 19.00 |  |
| Company-owned | 34.14 (2.61) | 35.44 (5.38) | -0.2 | 34.10 | 35.40 |  |

## 2. Means in wave 1

| Item | NJ | PA | t | Paper NJ | Paper PA | Paper t |
|------|----|----|---|----------|----------|---------|
| FTE employment | 20.44 (0.51) | 23.33 (1.35) | -2.0 | 20.40 | 23.30 | -2.0 |
| % full-time employees (incl. managers) | 37.73 (1.14) | 38.76 (2.30) | -0.4 | 32.80 | 35.90 | -1.0 |
| Starting wage | 4.61 (0.02) | 4.63 (0.04) | -0.4 | 4.61 | 4.63 | -0.4 |
| Wage = $4.25 (%, all stores) | 30.51 (2.53) | 32.91 (5.29) | -0.4 | 30.50 | 32.90 | -0.4 |
| Price of full meal | 3.35 (0.04) | 3.04 (0.07) | 4.0 | 3.35 | 3.04 | 3.9 |
| Hours open (weekday) | 14.42 (0.15) | 14.53 (0.33) | -0.3 | 14.40 | 14.50 | -0.3 |
| Recruiting bonus (%) | 23.56 (2.33) | 29.11 (5.11) | -1.0 | 23.60 | 29.10 | -1.0 |

## 3. Means in wave 2

| Item | NJ | PA | t | Paper NJ | Paper PA | Paper t |
|------|----|----|---|----------|----------|---------|
| FTE employment | 21.03 (0.52) | 21.17 (0.94) | -0.1 | 21.00 | 21.20 | -0.2 |
| % full-time employees (incl. managers) | 40.76 (1.26) | 35.60 (2.40) | 1.9 | 35.90 | 30.40 | 1.8 |
| Starting wage | 5.08 (0.01) | 4.62 (0.04) | 10.8 | 5.08 | 4.62 | 10.8 |
| Wage = $4.25 (%, all stores) | 0.00 (0.00) | 25.32 (4.89) | -5.2 | 0.00 | 25.30 |  |
| Wage = $5.05 (%, all stores) | 85.50 (1.94) | 1.27 (1.26) | 36.5 | 85.20 | 1.30 | 36.1 |
| Price of full meal | 3.41 (0.04) | 3.03 (0.07) | 5.1 | 3.41 | 3.03 | 5.0 |
| Hours open (weekday) | 14.42 (0.15) | 14.65 (0.33) | -0.6 | 14.40 | 14.70 | -0.8 |
| Recruiting bonus (%) | 20.32 (2.27) | 23.38 (4.82) | -0.6 | 20.30 | 23.40 | -0.6 |

## Definitions and methods

- FTE (before) = EMPFT + NMGRS + 0.5 * EMPPT; FTE (after) uses the '2'-suffix variables. Permanent closure (STATUS2 = 3) -> after FTE = 0; temporary closure (STATUS2 in {2, 4, 5}) -> after FTE missing.
- Full meal price = PSODA + PFRY + PENTREE (wave 2: PSODA2 + PFRY2 + PENTREE2); missing if any component is missing.
- Recruiting bonus = BONUS (wave 1) and SPECIAL2 (wave 2). SPECIAL2 reproduces the paper's wave-2 bonus shares exactly (NJ 20.3, PA 23.4), so it is taken as the wave-2 bonus field (not assumed from its label).
- `% full-time employees`: computed including managers as (EMPFT + NMGRS) / (EMPFT + NMGRS + EMPPT), consistent with the paper's FTE note that 'full-time workers' includes managers. This is the value shown above; it does NOT match the paper's printed 32.8 / 35.9 / 30.4, so the paper's exact % full-time definition is UNCONFIRMED. The managers-excluded variant (EMPFT / (EMPFT + EMPPT)) is reported in a separate diagnostic table below; it also does not match.
- Each metric uses its own valid sample; no unified row deletion.

## Standard errors and t-test

- Continuous variable: SEM = sample sd / sqrt(n).
- Percentage: SE = sqrt(p (1 - p) / n) * 100.
- Two-state comparison: t = (m_NJ - m_PA) / sqrt(se_NJ^2 + se_PA^2), a two-sample test of equality of means (independent states, unequal variance / unpooled proportions).

## Known differences from the paper

- **`wage = X` denominators.** For 'wage = $4.25' and 'wage = $5.05' two denominators are reported -- every store in the state (missing wage treated as 'not equal to X') and valid wage records only (missing excluded) -- see the diagnostic section below. The all-stores denominator is the one that matches the paper's printed percentages, except NJ wave-2 'wage = $5.05' (see below). The original raw missing values are not modified, and the authors' original code is not claimed to have been verified.
- **% full-time employees.** Definition unconfirmed (see above); the computed values differ from the paper's, so this row is NOT treated as replicated.
- Store-type rows are reported without standard errors or t-tests in the paper; this replication computes them for completeness, and the proportions match the printed values exactly.

## Diagnostic: `wage = X` under two denominators

For each 'wage = X' cell the numerator (count == X), the two denominators (all stores in the state vs. valid wage records), the number of missing wages, the percentage (SE), and the two-state t are shown. 'Match' compares the rounded percentage to the paper's printed value. The numerator is identical for the two denominators (a missing wage can never equal X); only the denominator differs.

**Wave 1 -- Wage = $4.25 (%) (target = 4.25)**

| State | Denominator | count == X | N (denom) | missing | % (SE) |
|---|---|---|---|---|---|
| NJ | all stores | 101 | 331 | 17 | 30.51 (2.53) |
| NJ | valid wage | 101 | 314 | 17 | 32.17 (2.64) |
| PA | all stores | 26 | 79 | 3 | 32.91 (5.29) |
| PA | valid wage | 26 | 76 | 3 | 34.21 (5.44) |

t (NJ-PA): all stores = -0.4, valid wage = -0.3; paper t = -0.4. Paper: NJ 30.5, PA 32.9. Match (all stores): NJ yes, PA yes; match (valid wage): NJ no, PA no.

**Wave 2 -- Wage = $4.25 (%) (target = 4.25)**

| State | Denominator | count == X | N (denom) | missing | % (SE) |
|---|---|---|---|---|---|
| NJ | all stores | 0 | 331 | 13 | 0.00 (0.00) |
| NJ | valid wage | 0 | 318 | 13 | 0.00 (0.00) |
| PA | all stores | 20 | 79 | 8 | 25.32 (4.89) |
| PA | valid wage | 20 | 71 | 8 | 28.17 (5.34) |

t (NJ-PA): all stores = -5.2, valid wage = -5.3; paper t not reported. Paper: NJ 0.0, PA 25.3. Match (all stores): NJ yes, PA yes; match (valid wage): NJ yes, PA no.

**Wave 2 -- Wage = $5.05 (%) (target = 5.05)**

| State | Denominator | count == X | N (denom) | missing | % (SE) |
|---|---|---|---|---|---|
| NJ | all stores | 283 | 331 | 13 | 85.50 (1.94) |
| NJ | valid wage | 283 | 318 | 13 | 88.99 (1.76) |
| PA | all stores | 1 | 79 | 8 | 1.27 (1.26) |
| PA | valid wage | 1 | 71 | 8 | 1.41 (1.40) |

t (NJ-PA): all stores = 36.5, valid wage = 39.0; paper t = 36.1. Paper: NJ 85.2, PA 1.3. Match (all stores): NJ no, PA yes; match (valid wage): NJ no, PA no.

- **NJ wave-2 'wage = $5.05'.** The all-stores denominator gives 85.50% (283 / 331), while the paper prints 85.2% (equal to 282 / 331). The public data contain 283 NJ wave-2 records at exactly $5.05; one of them (sheet 65) is a temporarily closed store (STATUS2 = 2). Whether the paper excludes that store is unconfirmed; the raw value is left unchanged.

## Diagnostic: % full-time excluding managers

For checking the unconfirmed definition, the managers-excluded variant (EMPFT / (EMPFT + EMPPT)) is:

| Wave | NJ mean | NJ n | PA mean | PA n |
|------|---------|------|---------|------|
| 1 | 28.63 | 326 | 30.29 | 78 |
| 2 | 32.01 | 315 | 26.02 | 76 |
