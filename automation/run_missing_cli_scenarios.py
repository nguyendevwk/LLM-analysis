"""Resume full CLI scenarios without rerunning completed experiment cells."""

import argparse
import json
import logging
from pathlib import Path

import model_registry
from cli_experiment_runner import CLIExperimentRunner

STRATEGIES = ("simple_prompting", "chain_of_thought_prompting")
CONTEXTS = ("interface", "interface_docstring", "full_context")

logger = logging.getLogger("run_missing_cli_scenarios")


def _is_completed(run_dir: Path) -> bool:
    """Treat a run as complete when its analysis report is valid JSON."""
    report = run_dir / "analysis_results.json"
    if not report.is_file():
        return False
    try:
        json.loads(report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return True


def _discover_models(results_dir: Path) -> list[str]:
    models: set[str] = set()
    for strategy in STRATEGIES:
        for context in CONTEXTS:
            cell = results_dir / strategy / context
            if cell.is_dir():
                models.update(path.name for path in cell.iterdir() if path.is_dir())
    return sorted(models)


def _registered_models() -> list[str]:
    return sorted(model_registry.REGISTRY)


def _missing_runs(results_dir: Path, model: str, run_count: int) -> list[tuple[int, str, str]]:
    missing = []
    for run_id in range(1, run_count + 1):
        for strategy in STRATEGIES:
            for context in CONTEXTS:
                run_dir = (
                    results_dir / strategy / context / model / f"run_{run_id:03d}"
                )
                if not _is_completed(run_dir):
                    missing.append((run_id, strategy, context))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run only missing cells in a 10-run full-scenario matrix."
    )
    parser.add_argument("--results-dir", default="cli_results_v1")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--model", action="append", dest="models")
    parser.add_argument(
        "--all-registered",
        action="store_true",
        help="Include every model in model_registry, not only models already in results.",
    )
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")

    results_dir = Path(args.results_dir)
    models = sorted(
        set(args.models or [])
        or (_registered_models() if args.all_registered else _discover_models(results_dir))
    )
    if not models:
        parser.error("No models found; pass --model or --all-registered")

    pending = {
        model: _missing_runs(results_dir, model, args.runs) for model in models
    }
    total = sum(len(items) for items in pending.values())
    logger.info("Models: %s", ", ".join(models))
    logger.info("Missing experiment cells: %d", total)
    if total == 0:
        logger.info("All requested runs are already complete.")
        return 0

    completed = 0
    failed = 0
    for model in models:
        for run_id, strategy, context in pending[model]:
            logger.info(
                "Running %d/%d: model=%s run=%03d strategy=%s context=%s",
                completed + failed + 1,
                total,
                model,
                run_id,
                strategy,
                context,
            )
            runner = CLIExperimentRunner(
                base_results_dir=results_dir,
                run_id=run_id,
            )
            result = runner.run_single_experiment(model, strategy, context)
            if result and _is_completed(
                results_dir
                / strategy
                / context
                / model
                / f"run_{run_id:03d}"
            ):
                completed += 1
            else:
                failed += 1
                logger.error(
                    "Run did not produce a valid analysis report: %s run_%03d",
                    model,
                    run_id,
                )

    logger.info("Finished: %d completed, %d failed", completed, failed)
    return 1 if failed else 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    )
    raise SystemExit(main())
