#!/usr/bin/env python3
"""
Council Runner entrypoint inside kaggle/ directory.
Enables running `python council_runner.py` directly from within the kaggle/ folder.
"""

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(REPO_ROOT / "automation"))

from kaggle.kaggle_dual_gpu_runner import (
    CouncilEngine,
    DualGPUEngine,
    run_council_pipeline,
    run_full_scenario_benchmark,
    run_quality_gates,
    check_gpu_environment,
    ensure_bitsandbytes,
    main,
)

__all__ = [
    "CouncilEngine",
    "DualGPUEngine",
    "run_council_pipeline",
    "run_full_scenario_benchmark",
    "run_quality_gates",
    "check_gpu_environment",
    "ensure_bitsandbytes",
]

if __name__ == "__main__":
    main()
