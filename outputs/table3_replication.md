# Card & Krueger (1994) Table 3 replication

Mean FTE employment by state and, within New Jersey, by wave-1 starting-wage group. Standard errors are in parentheses.

| Row | PA | NJ | NJ-PA | Wage=$4.25 | Wage=$4.26-$4.99 | Wage>=$5.00 | Low-high | Mid-high |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 1. FTE before, all available | 23.33 (1.35) | 20.44 (0.51) | -2.89 (1.44) | 19.56 (0.77) | 20.08 (0.84) | 22.25 (1.14) | -2.69 (1.37) | -2.17 (1.41) |
| 2. FTE after, all available | 21.17 (0.94) | 21.03 (0.52) | -0.14 (1.08) | 20.88 (1.01) | 20.96 (0.76) | 20.21 (1.03) | 0.66 (1.44) | 0.74 (1.27) |
| 3. Change in mean FTE | -2.17 (NA) | 0.59 (NA) | 2.75 (NA) | 1.32 (NA) | 0.87 (NA) | -2.04 (NA) | 3.36 (NA) | 2.91 (NA) |
| 4. Change, balanced sample | -2.28 (1.25) | 0.47 (0.48) | 2.75 (1.34) | 1.20 (0.82) | 0.71 (0.69) | -2.16 (1.01) | 3.36 (1.30) | 2.87 (1.22) |
| 5. Change, temp. closures set to 0 | -2.28 (1.25) | 0.23 (0.49) | 2.51 (1.35) | 0.90 (0.87) | 0.49 (0.69) | -2.39 (1.02) | 3.29 (1.34) | 2.88 (1.23) |

## Sample and closure rules

- Rows 1 and 2 use each period's own valid sample (a store needs valid FTE in that period only; it need not appear in both periods).
- Rows 4 and 5 use the balanced sample (a store contributes only when its FTE is valid in both waves).
- FTE = full-time + managers + 0.5 * part-time; a missing component leaves FTE missing (never filled with zero).
- STATUS2 = 3 (permanent closure): after FTE set to 0 (6 stores).
- STATUS2 in {2, 4, 5} (temporary closure): after FTE treated as missing in rows 1-4 (4 stores).
- Row 5 only: temporarily closed stores get after FTE = 0, then the balanced sample is re-determined and the per-store change is averaged.
- Refusals and any other missing data are never imputed to zero.
- Wage columns use the NJ wave-1 starting wage; stores with a missing wage are excluded from wage columns but kept in the state columns.

## Standard errors

- Rows 1-2: SEM of the level values.
- Rows 4-5: SEM of the per-store change values (balanced sample), i.e. the store-level change is treated as the unit of observation.
- Row 3: the original paper's standard-error formula is **unconfirmed (to verify)**, so all eight row-3 SEs are reported as NA in the main table.
- Difference-column SEs (NJ-PA, low-high, mid-high) are sqrt(se_a^2 + se_b^2), treating the two groups as independent (valid for PA vs NJ and across wage groups); this applies to rows 1, 2, 4, and 5 only.

## Row 3 standard errors: naive diagnostic (not for significance)

Values below use the naive independent-sample approximation sqrt(se_before^2 + se_after^2). They are retained only for diagnosis; they do not match the paper's row-3 SE (e.g. the paper's NJ-PA SE is 1.36 while the naive value is 1.80), and must not be used for significance conclusions.

| Column | PA | NJ | NJ-PA | Wage=$4.25 | Wage=$4.26-$4.99 | Wage>=$5.00 | Low-high | Mid-high |
|--------|--------|--------|--------|--------|--------|--------|--------|--------|
| Naive row-3 SE | 1.65 | 0.73 | 1.80 | 1.27 | 1.13 | 1.53 | 1.99 | 1.90 |

## Wage-range check

- No NJ store has a starting wage below $4.25 (all in range).
- NJ stores with missing starting wage (excluded from wage columns): 17.

## Comparison with the paper

- All cells are computed. The main point estimates and the balanced sample (rows 1, 2, 4, 5) are close to or match the paper; row-3 standard errors are not yet reproduced.
- Column definitions and wage-group counts match the paper's footnotes (low N=101, mid N=140, high N=73; six closed stores set to 0; four temporary closures treated as missing).
- Row 4 NJ-PA (balanced DiD) matches the paper's 2.75 (1.34).
- Row 5 NJ-PA (temporary closures set to 0) is 2.51 (1.35).
- Row 3 NJ-PA: the paper reports 2.76 (1.36); this replication computes 2.75360578, which rounds to 2.75. The cause of this difference is not yet confirmed, so it is recorded here rather than dismissed as rounding.
