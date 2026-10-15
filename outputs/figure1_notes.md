# Card & Krueger (1994) Figure 1 replication notes

Distribution of starting wages, New Jersey vs. Pennsylvania. Two panels: February 1992 (before, WAGE_ST) and November 1992 (after, WAGE_ST2).

## Missing-data handling

- A store is included in a state-period distribution whenever its starting wage is present; employment data play no role here.
- Missing wages are excluded and are never filled with zero.
- The denominator for a state-period is its own count of valid wage observations (not a common or employment-based total).

## Binning (centered on the x-axis tick labels)

- The original scan marks the x-axis at 4.25, 4.35, ..., 5.55 but does not state the bin boundaries or the tail rule in text.
- This replication centers each 10-cent bin on its tick label, so the bins are [4.20, 4.30), [4.30, 4.40), ..., [5.50, 5.60), left-closed and right-open.
- Centering matters: the $4.50 cluster (a tall ~16-17% bar in each state) falls in the [4.50, 4.60) bin whose center and label is 4.55, not in a [4.45, 4.55) bin labeled 4.45.
- Wages are binned on integer cents (round(wage * 100)) to avoid floating-point boundary errors.

## Range / tail check

- No observed starting wage is below $4.20, so nothing is dropped on the low end.
- The original axis ends at 5.55, so wages at or above $5.60 fall off the right edge and are excluded (not drawn as an open bin). Wage minima/maxima and excluded counts per state-period:

| Period | State | n | min | max | excluded >=5.60 |
|---|---|---|---|---|---|
| February 1992 | New Jersey | 314 | 4.25 | 5.75 | 2 |
| February 1992 | Pennsylvania | 76 | 4.25 | 5.50 | 0 |
| November 1992 | New Jersey | 318 | 5.00 | 5.75 | 3 |
| November 1992 | Pennsylvania | 71 | 4.25 | 6.25 | 1 |

## Percent sums

- Percentages sum to just under 100 per state-period because the few wages at or above $5.60 (off the original's right edge) are excluded.

| Period | State | sum of percents |
|---|---|---|
| before | New Jersey | 99.3631 |
| before | Pennsylvania | 100.0000 |
| after | New Jersey | 99.0566 |
| after | Pennsylvania | 98.5915 |

## Layout

- Two stacked panels (February 1992 on top, November 1992 on the bottom), each with side-by-side bars for New Jersey and Pennsylvania.
- Each panel has its own y-axis scale, mirroring the original figure: 0-35 percent for February 1992 and 0-90 percent for November 1992.
- Axis labels follow the original: y-axis 'Percent', x-axis 'Wage Range', and x-axis ticks at the bin centers 4.25, 4.35, ..., 5.55 (the axis ends at 5.55, matching the original).

## Differences from the original figure

- Wages at or above $5.60 fall off the original's right edge and are excluded (6 of 779 valid wage observations). These are reported in 'Range / tail check' above, never dropped silently.
- Bar colors, spacing, and layout are this replication's choices; the figure was not reverse-engineered from the original's bar heights.
