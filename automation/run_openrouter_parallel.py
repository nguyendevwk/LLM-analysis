"""Run missing OpenRouter experiment cells in parallel using independent keys."""

import argparse
import json
import logging
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

STRATEGIES = ("simple_prompting", "chain_of_thought_prompting")
CONTEXTS = ("interface", "interface_docstring", "full_context")
MODEL = "openrouter-nemotron-3-super-120b-a12b"
logger = logging.getLogger("run_openrouter_parallel")


def is_complete(path: Path) -> bool:
    report = path / "analysis_results.json"
    try:
        json.loads(report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return True


def missing_tasks(root: Path, runs: int) -> list[tuple[int, str, str]]:
    tasks = []
    for run_id in range(1, runs + 1):
        for strategy in STRATEGIES:
            for context in CONTEXTS:
                path = root / strategy / context / MODEL / f"run_{run_id:03d}"
                if not is_complete(path):
                    tasks.append((run_id, strategy, context))
    return tasks


def run_task(
    root: Path, task: tuple[int, str, str], key_slot: int
) -> tuple[tuple[int, str, str], int, bool]:
    run_id, strategy, context = task
    env = os.environ.copy()
    env["OPENROUTER_API_KEY_SLOT"] = str(key_slot)
    command = [
        sys.executable,
        "automation/cli_experiment_runner.py",
        "--model",
        MODEL,
        "--strategy",
        strategy,
        "--context",
        context,
        "--run-id",
        str(run_id),
        "--results-dir",
        str(root),
    ]
    logger.info(
        "Starting key %d: run=%03d strategy=%s context=%s",
        key_slot,
        run_id,
        strategy,
        context,
    )
    completed = subprocess.run(command, env=env, text=True)
    report = root / strategy / context / MODEL / f"run_{run_id:03d}"
    return task, completed.returncode, is_complete(report)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resume missing OpenRouter runs with per-key workers."
    )
    parser.add_argument("--results-dir", default="automation/cli_results_v1")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List missing cells and key assignments without making requests.",
    )
    parser.add_argument(
        "--key-slots",
        default="1,2",
        help="Comma-separated OPENROUTER_API_KEY slots assigned to workers.",
    )
    args = parser.parse_args()
    if args.runs < 1 or args.workers < 1:
        parser.error("--runs and --workers must be positive")

    try:
        key_slots = [int(value.strip()) for value in args.key_slots.split(",")]
    except ValueError as error:
        parser.error(f"invalid --key-slots: {error}")
    if not key_slots or len(set(key_slots)) != len(key_slots):
        parser.error("--key-slots must contain unique integers")
    if len(key_slots) < args.workers:
        parser.error("provide at least one unique key slot per worker")

    root = Path(args.results_dir)
    tasks = missing_tasks(root, args.runs)
    logger.info("OpenRouter missing cells: %d", len(tasks))
    if not tasks:
        return 0
    if args.dry_run:
        for index, task in enumerate(tasks):
            logger.info("key %d -> run=%03d strategy=%s context=%s",
                        key_slots[index % args.workers], task[0], task[1], task[2])
        return 0

    failures = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(run_task, root, task, key_slots[index % args.workers]): task
            for index, task in enumerate(tasks)
        }
        for future in as_completed(futures):
            task, returncode, complete = future.result()
            if returncode or not complete:
                failures += 1
                logger.error(
                    "Failed task %s (exit %d, valid_report=%s)",
                    task,
                    returncode,
                    complete,
                )

    logger.info("Finished: %d tasks, %d failed", len(tasks), failures)
    return 1 if failures else 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    )
    raise SystemExit(main())
