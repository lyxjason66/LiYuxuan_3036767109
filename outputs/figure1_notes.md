# Card & Krueger (1994) Figure 1 replication notes

Distribution of starting wages, New Jersey vs. Pennsylvania. Two panels: February 1992 (before, WAGE_ST) and November 1992 (after, WAGE_ST2).

## Missing-data handling

- A store is included in a state-period distribution whenever its starting wage is present; employment data play no role here.
- Missing wages are excluded and are never filled with zero.
- The denominator for a state-period is its own count of valid wage observations (not a common or employment-based total).

## Binning (a replication choice)

- The original scan marks the x-axis at 4.25, 4.35, ..., 5.55 but does not state the bin boundaries or the tail rule, so the exact original binning is NOT confirmed here.
- This replication uses 10-cent bins [4.25, 4.35), [4.35, 4.45), ..., [5.45, 5.55), left-closed and right-open, plus an open top bin [5.55, +infinity).
- A wage of exactly $5.05 falls in the [5.05, 5.15) bin (left-closed). This is a share of an interval, not a 'wage that rounds to 5.05' count; the two are not conflated.
- Wages are binned on integer cents (round(wage * 100)) to avoid floating-point boundary errors.

## Range / tail check

- No observed starting wage is below $4.25, so nothing is dropped on the low end.
- The data extend above the last 10-cent bin, so the open top bin [5.55, +infinity) captures those values rather than dropping them. Wage minima/maxima per state-period:

| Period | State | n | min | max |
|---|---|---|---|---|
| February 1992 (before) | New Jersey | 314 | 4.25 | 5.75 |
| February 1992 (before) | Pennsylvania | 76 | 4.25 | 5.50 |
| November 1992 (after) | New Jersey | 318 | 5.00 | 5.75 |
| November 1992 (after) | Pennsylvania | 71 | 4.25 | 6.25 |

## Percent sums

- Percentages should sum to about 100 per state-period (float rounding may give 99.99/100.01).

| Period | State | sum of percents |
|---|---|---|
| before | New Jersey | 100.0000 |
| before | Pennsylvania | 100.0000 |
| after | New Jersey | 100.0000 |
| after | Pennsylvania | 100.0000 |

## Differences from the original figure

- The open top bin is labeled '>=5.55' (the original only marks '5.55'); this makes the tail treatment explicit.
- Bar colors, spacing, and layout are this replication's choices; the figure was not reverse-engineered from the original's bar heights.
