# Card & Krueger (1994) — Minimum Wages and Employment: replication

Replication of Card & Krueger (1994), "Minimum Wages and Employment: A Case
Study of the Fast-Food Industry in New Jersey and Pennsylvania" (*American
Economic Review*), using the store-level survey data in `data/public.csv`.

The analysis reproduces the paper's Table 2 (store characteristics), Table 3
(difference-in-differences estimates), Table 4 (reduced-form OLS) and Figure 1
(wage distribution), plus one supplementary sensitivity check that excludes
permanently closed restaurants. This is a replication exercise: some printed
values are matched exactly and a few remain different — see "Known differences"
below.

## Data source and access

- The input is `data/public.csv`: 410 store-level observations (46 columns) of
  the Card & Krueger fast-food restaurant survey. Column definitions are in
  `DATA_DICTIONARY.md`.
- The file comes from the course data package **`01_DID.zip`** (restaurant
  survey data). Extract the ZIP and place `public.csv` at `data/public.csv`;
  keep the filename unchanged.
- The data are provided for the course project under the applicable data-access
  terms. Do **not** publish the raw `public.csv` to a public repository;
  document its location and access requirements instead. No public download
  link is known for this file, so none is given here.

## Requirements

- Python 3 with the packages in `requirements.txt` (`numpy`, `matplotlib`,
  `statsmodels`). Install with:

  ```bash
  pip install -r requirements.txt
  ```

  The committed outputs were produced with the conda interpreter
  `/opt/miniconda3/bin/python3`.

## Directory structure

```
.
├── run_all.py                  # unified entry point (runs everything in order)
├── requirements.txt            # direct third-party dependencies
├── README.md
├── DATA_DICTIONARY.md          # column definitions for public.csv
├── report.pdf                  # final written report
├── AI_USE.md                   # AI usage disclosure
├── data/
│   ├── public.csv              # input data (NOT tracked by git)
│   └── processed/              # local-only, git-ignored
│       └── store_level.csv     # generated restaurant-level processed data
├── scripts/
│   ├── card_common.py          # shared data loading + FTE rules (single source of truth)
│   ├── export_processed.py     # writes the per-store processed dataset
│   ├── replicate_table2.py
│   ├── replicate_table3.py
│   ├── replicate_table4.py
│   ├── replicate_figure1.py
│   └── extension_closures.py   # supplementary sensitivity check
└── outputs/                    # generated CSV / Markdown / PNG results
    ├── table2_replication.{csv,md}
    ├── table3_replication.{csv,md}
    ├── table4_replication.{csv,md}
    ├── figure1_wage_distribution.{csv,png}
    ├── extension_closures.{csv,md}
    └── validation_summary.md   # matched vs. remaining differences
```

## Running

The single command below regenerates every output in order — first the local
restaurant-level processed dataset, then Table 2 → Table 3 → Table 4 →
Figure 1 → closure extension — using the same Python interpreter for each
step. If any step fails, the run stops immediately and prints the error.

```bash
python3 run_all.py
```

The runner resolves all paths from its own location, so it can be invoked from
any working directory. Each step can also be run on its own, e.g.
`python3 scripts/replicate_table4.py`. This running procedure is the reusable
workflow for the whole project.

The run also writes `data/processed/store_level.csv` — a restaurant-level
processed dataset (identifiers, analysis variables, constructed FTE / GAP
variables, and per-analysis sample markers) generated locally. This directory
is git-ignored: the file is produced on the user's machine and is not
committed. Generating it locally and sharing it are separate questions — the
file is always generated locally; whether it may be included when submitting
the assignment still depends on the course data-use permission.

## Outputs

- `outputs/table2_replication.md` / `.csv` — Table 2: store-type shares and
  wave-1 / wave-2 means, with the replication's computed values and the paper's
  printed values side by side.
- `outputs/table3_replication.md` / `.csv` — Table 3: per-store employment
  changes and the NJ−PA difference (DiD).
- `outputs/table4_replication.md` / `.csv` — Table 4: reduced-form OLS on the
  357-store primary sample (the 351-store full-wage sample is a supplementary
  result).
- `outputs/figure1_wage_distribution.png` / `.csv` — Figure 1: wage
  distribution.
- `outputs/extension_closures.md` / `.csv` — supplementary sensitivity check
  excluding permanently closed restaurants.
- `outputs/validation_summary.md` — what matches the paper, what remains
  different, and which definitions are still unconfirmed.

## Known differences / not yet replicated

See `outputs/validation_summary.md` for details. In brief:

- **Table 2, NJ wave-2 `wage = $5.05`** — 85.50% (283/331) vs. the paper's
  85.2% (282/331); cause not confirmed.
- **Table 4, model (v)** — 11.98 vs. the paper's 11.91; cause not confirmed.
- **Table 2, `% full-time employees`** — definition unconfirmed; neither the
  managers-included nor the managers-excluded formula reproduces 32.8 / 35.9 /
  30.4.
- **Table 3, row-3 standard errors** — not yet reproduced (the original SE
  formula is unconfirmed).
- **Figure 1 bin boundaries** — the original rule is not stated in the scan;
  the 10-cent bins are a documented replication choice (see
  `outputs/figure1_notes.md`).

## Report and AI usage

- [report.pdf](report.pdf) — the final written report.
- [AI_USE.md](AI_USE.md) — AI usage disclosure.
