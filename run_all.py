#!/usr/bin/env python3
"""Unified entry point for the Card & Krueger (1994) replication.

Runs every analysis script in a fixed order with this same Python interpreter:

    processed data    ->  export_processed.py
    Table 2          ->  replicate_table2.py
    Table 3          ->  replicate_table3.py
    Table 4          ->  replicate_table4.py
    Figure 1         ->  replicate_figure1.py
    closure extension -> extension_closures.py

Each script writes its own outputs under ``outputs/``. If any step fails the
runner stops immediately, reports the failing step, and exits with the child's
exit code. Paths are resolved from this file's location, so the command works
from any working directory.

The child processes run in isolated mode (``-I``): this ignores the user
site-packages and PYTHONPATH, which is the documented safety default for
reading the untrusted downloaded data file, while still using the conda
environment's site-packages.

Usage:

    python3 run_all.py
"""

import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")

# Run order: data export first, then the paper's tables / figure, then the
# extension.
STEPS = [
    ("processed data", "export_processed.py"),
    ("Table 2", "replicate_table2.py"),
    ("Table 3", "replicate_table3.py"),
    ("Table 4", "replicate_table4.py"),
    ("Figure 1", "replicate_figure1.py"),
    ("closure extension", "extension_closures.py"),
]


def main():
    interpreter = sys.executable
    print(f"Using interpreter: {interpreter}", flush=True)
    for label, filename in STEPS:
        script = os.path.join(SCRIPTS_DIR, filename)
        print(f"\n==> {label}: {filename}", flush=True)
        result = subprocess.run([interpreter, "-I", script], cwd=PROJECT_ROOT)
        if result.returncode != 0:
            print(
                f"FAILED: {label} ({filename}) exited with code "
                f"{result.returncode}",
                file=sys.stderr,
                flush=True,
            )
            sys.exit(result.returncode)
    print("\nAll steps completed successfully.", flush=True)


if __name__ == "__main__":
    main()
