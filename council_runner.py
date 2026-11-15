#!/usr/bin/env python3
"""
Council Runner - Entrypoint for Kaggle Dual-GPU Council Test Generation.

Exposes CouncilEngine and CLI commands for automated testing.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "kaggle"))
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
