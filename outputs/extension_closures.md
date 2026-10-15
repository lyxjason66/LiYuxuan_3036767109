# Sensitivity check: excluding permanently closed restaurants

Research question: is the NJ vs. PA difference in the per-store change in full-time-equivalent employment still similar when the permanently closed restaurants are dropped?

## Sample rules

- **Baseline** = the Table 3 row-4 balanced sample: FTE valid in both waves, with a permanently closed store (STATUS2 = 3) set to after-FTE = 0 and a temporarily closed store (after-FTE missing) excluded.
- **Excluding permanent closures** = the baseline sample minus stores with STATUS2 = 3. All other missing-value and temporary-closure rules are unchanged.

## Results

| Sample | State | N | Mean change | SE |
|--------|-------|---|-------------|----|
| baseline | NJ | 309 | 0.4667 | 0.4808 |
| baseline | PA | 75 | -2.2833 | 1.2533 |
| excluding_permanent_closures | NJ | 304 | 0.6577 | 0.4810 |
| excluding_permanent_closures | PA | 74 | -2.0642 | 1.2508 |

| Sample | DiD (NJ - PA) | DiD SE |
|--------|---------------|--------|
| baseline | 2.7500 | 1.3423 |
| excluding_permanent_closures | 2.7219 | 1.3401 |

## Stores excluded (permanently closed, STATUS2 = 3)

- NJ: 5 store(s) in the balanced sample were permanently closed.
- PA: 1 store(s) in the balanced sample were permanently closed.
- The counts above are the stores actually present in the baseline sample, not an assumed count.

## Limitations

- Dropping permanently closed restaurants removes the employment loss caused by closure, so this is a **supplementary sensitivity check**, not a substitute for the main result.
- The two estimates use overlapping samples, so they are NOT treated as independent estimates and no difference test between them is reported.
- The result is reported as computed; non-significance is not interpreted as 'no effect'.
