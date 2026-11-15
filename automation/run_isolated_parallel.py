"""Run missing experiment cells in isolated per-worker source copies.

Each worker owns a workspace containing a private copy of the automation
source, a private ``mutants/`` directory (so mutmut caches never clash), the
``order_calculator.py`` subject and the ``.env`` file. Workers receive
disjoint cell lists and write their results directly into the canonical
results directory through an absolute ``--results-dir``, so no merge step is
needed afterwards.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import model_registry

REPO_ROOT = Path(__file__).resolve().parents[1]
STRATEGIES = ("simple_prompting", "chain_of_thought_prompting")
CONTEXTS = ("interface", "interface_docstring", "full_context")
DEFAULT_MODELS = (
    "gemini-api-3.5-flash-lite",  # quota is tightest here — run it first
    "openrouter-nemotron-3-super-120b-a12b",
)
PROVIDER_KEY_ENV = {
    "gemini": "GEMINI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "groq": "GROQ_API_KEY",
    "local": "LOCAL_API_KEY",
}
PROVIDER_BASE_URL = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai",
    "openrouter": "https://openrouter.ai/api/v1",
    "groq": "https://api.groq.com/openai/v1",
}
COPY_IGNORE = shutil.ignore_patterns(
    "cli_results*", "prompts_results", "__pycache__", "*.log", ".DS_Store",
)
ERROR_MARKERS = (
    "rate limit", "quota", " 429", "429:", "no api key", "no gemini",
    "no openrouter", "invalid api key", "runtimeerror", "traceback",
)

logger = logging.getLogger("run_isolated_parallel")


@dataclass(frozen=True)
class Task:
    model: str
    run_id: int
    strategy: str
    context: str

    @property
    def provider(self) -> Optional[str]:
        resolved = model_registry.resolve_model(self.model)
        return resolved[0].provider if resolved else None

    def label(self) -> str:
        return (
            f"model={self.model} run={self.run_id:03d} "
            f"strategy={self.strategy} context={self.context}"
        )


@dataclass
class TaskResult:
    task: Task
    returncode: int
    complete: bool
    reason: str = ""


def is_complete(path: Path) -> bool:
    """A cell counts as done only when its analysis report parses as JSON."""
    try:
        json.loads((path / "analysis_results.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return True



def env_names() -> set[str]:
    """Names (never values) from the process environment and the repo .env."""
    names = set(os.environ)
    env_file = REPO_ROOT / ".env"
    if env_file.is_file():
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            names.add(line.partition("=")[0].strip())
    return names


def load_env_dict() -> Dict[str, str]:
    """KEY=VALUE pairs from the repo .env overlaid by the process environment."""
    merged: Dict[str, str] = {}
    env_file = REPO_ROOT / ".env"
    if env_file.is_file():
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                merged.setdefault(key, value)
    for key, value in os.environ.items():
        if value:
            merged[key] = value
    return merged


def probe_key_health(prefix: str, slots: Sequence[int], model: str,
                     base_url: str, timeout: int = 25) -> Tuple[List[int], List[str]]:
    """Classify key slots with one tiny request each (value never logged).

    Slots answering 200 stay; 401/403 (bad key) and 429 (quota exhausted)
    are dropped; anything else (503/500/404/timeout) is kept as unknown.
    Returns (healthy_slots, human-readable report lines with names only).
    """
    try:
        import requests
    except ImportError:
        return list(slots), [f"{prefix}: requests unavailable, keeping all slots"]
    env = load_env_dict()
    healthy: List[int] = []
    report: List[str] = []
    for slot in slots:
        name = prefix if slot == 1 else f"{prefix}_{slot}"
        key = env.get(name)
        if not key:
            report.append(f"{name}: NOT CONFIGURED -> drop")
            continue
        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers={"Content-Type": "application/json",
                         "Authorization": f"Bearer {key}"},
                json={"model": model,
                      "messages": [{"role": "user", "content": "Say OK"}],
                      "max_tokens": 5},
                timeout=timeout,
            )
            if response.status_code == 200:
                healthy.append(slot)
                report.append(f"{name}: OK -> keep")
            elif response.status_code in (401, 403):
                report.append(f"{name}: HTTP {response.status_code} (bad key) -> drop")
            elif response.status_code == 429:
                report.append(f"{name}: HTTP 429 (quota exhausted) -> drop")
            else:
                healthy.append(slot)
                report.append(f"{name}: HTTP {response.status_code} (unknown) -> keep")
        except Exception as error:
            healthy.append(slot)
            report.append(f"{name}: probe error ({type(error).__name__}) -> keep")
        time.sleep(1)
    if not healthy:
        return list(slots), report + [f"{prefix}: all slots unusable, fallback to all"]
    return healthy, report


def available_slots(prefix: str, names: set[str]) -> List[int]:
    """Slot numbers configured for a key prefix (base name is slot 1)."""
    slots = [1] if prefix in names else []
    suffix = 2
    while f"{prefix}_{suffix}" in names:
        slots.append(suffix)
        suffix += 1
    return slots


def missing_tasks(results_dir: Path, models: Sequence[str], runs: int,
                  priority_order: Sequence[tuple[str, str]] | None = None
                  ) -> List[Task]:
    tasks: List[Task] = []
    for model in models:
        for run_id in range(1, runs + 1):
            for strategy in STRATEGIES:
                for context in CONTEXTS:
                    task = Task(model, run_id, strategy, context)
                    if not is_complete(cell_dir(results_dir, task)):
                        tasks.append(task)
    if priority_order:
        priority_index = {
            (s, c): i for i, (s, c) in enumerate(priority_order)
        }
        tasks.sort(key=lambda t: priority_index.get(
            (t.strategy, t.context), len(priority_order)))
    return tasks


def prepare_workspace(work_root: Path, index: int) -> Path:
    """Create a fresh isolated copy of the source tree for one worker."""
    workspace = work_root / f"w{index}"
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True)
    try:
        workspace.chmod(0o700)
    except OSError:
        pass

    shutil.copytree(REPO_ROOT / "automation", workspace / "automation",
                    ignore=COPY_IGNORE)
    shutil.copytree(REPO_ROOT / "mutants", workspace / "mutants",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(REPO_ROOT / "order_calculator.py", workspace / "order_calculator.py")

    # Legacy prompts live at <repo>/prompts_results/<strategy>/<context>/
    # prompt.txt; only these six files are read by prompt_strategies.
    for strategy in STRATEGIES:
        for context in CONTEXTS:
            prompt_file = (
                REPO_ROOT / "prompts_results" / strategy / context / "prompt.txt"
            )
            if not prompt_file.is_file():
                continue
            target_dir = workspace / "prompts_results" / strategy / context
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(prompt_file, target_dir / "prompt.txt")

    env_file = REPO_ROOT / ".env"
    if env_file.is_file():
        target = workspace / ".env"
        shutil.copy2(env_file, target)
        try:
            target.chmod(0o600)
        except OSError:
            pass

    (workspace / "logs").mkdir(exist_ok=True)
    return workspace


def failure_reason(log_file: Path) -> str:
    """Extract the most meaningful error line from a task log."""
    try:
        lines = [line.strip() for line in
                 log_file.read_text(encoding="utf-8", errors="replace").splitlines()]
    except OSError:
        return ""
    for line in reversed(lines):
        if any(marker in line.lower() for marker in ERROR_MARKERS):
            return line[:240]
    for line in reversed(lines):
        if line:
            return line[:240]
    return ""

def cell_dir(results_dir: Path, task: Task) -> Path:
    return (
        results_dir / task.strategy / task.context / task.model
        / f"run_{task.run_id:03d}"
    )

def run_task(
    workspace: Path,
    results_dir: Path,
    task: Task,
    slot_env: Optional[str],
    slot: Optional[int],
    timeout: int,
) -> TaskResult:
    env = os.environ.copy()
    automation_dir = str(workspace / "automation")
    env["PYTHONPATH"] = (
        automation_dir + os.pathsep + env["PYTHONPATH"]
        if env.get("PYTHONPATH") else automation_dir
    )
    if slot_env and slot:
        # Never let the shell's exported API key shadow the fresh .env value.
        for key_name in list(env):
            if key_name == slot_env or key_name.startswith(slot_env + "_"):
                del env[key_name]
        env_values = load_env_dict()
        key_name = slot_env if slot == 1 else f"{slot_env}_{slot}"
        key_value = env_values.get(key_name)
        if key_value:
            env[key_name] = key_value
        # api_client reads {PREFIX}_SLOT and picks PREFIX / PREFIX_N itself.
        env[f"{slot_env}_SLOT"] = str(slot)

    log_file = workspace / "logs" / (
        f"{task.model}__{task.strategy}__{task.context}__run{task.run_id:03d}.log"
    )
    command = [
        sys.executable,
        str(workspace / "automation" / "cli_experiment_runner.py"),
        "--model", task.model,
        "--strategy", task.strategy,
        "--context", task.context,
        "--run-id", str(task.run_id),
        "--results-dir", str(results_dir),
    ]
    logger.info("Starting [%s] %s", slot_env or "no-slot", task.label())
    returncode = 0
    try:
        with open(log_file, "w", encoding="utf-8") as handle:
            completed = subprocess.run(
                command, cwd=workspace, env=env, stdout=handle,
                stderr=subprocess.STDOUT, text=True, timeout=timeout,
            )
        returncode = completed.returncode
    except subprocess.TimeoutExpired:
        returncode = 124
    except OSError as error:
        returncode = 127
        log_file.write_text(f"spawn failed: {error}\n", encoding="utf-8")

    # The CLI exits 0 even when the experiment failed, so trust the report.
    complete = is_complete(cell_dir(results_dir, task))
    reason = "" if complete else failure_reason(log_file)
    if not complete:
        logger.error("Failed [%s] (exit %d): %s | %s",
                     slot_env or "no-slot", returncode, task.label(), reason)
    return TaskResult(task, returncode, complete, reason)


def run_worker(
    workspace: Path,
    results_dir: Path,
    tasks: Sequence[Task],
    slots_by_provider: Dict[str, Tuple[Optional[str], Optional[int]]],
    timeout: int,
) -> List[TaskResult]:
    results = []
    for task in tasks:
        slot_env, slot = slots_by_provider.get(task.provider or "", (None, None))
        results.append(
            run_task(workspace, results_dir, task, slot_env, slot, timeout)
        )
    return results


def split_round_robin(tasks: Sequence[Task], workers: int) -> List[List[Task]]:
    return [list(tasks[index::workers]) for index in range(workers)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resume missing cells in isolated per-worker copies."
    )
    parser.add_argument("--results-dir", default="automation/cli_results_v1")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--workers", type=int, default=2,
                        help="Number of parallel workers (default: 2 to avoid provider spam).")
    parser.add_argument(
        "--task-delay", type=int, default=30,
        help="Delay in seconds between consecutive task executions (prevents API rate limits).",
    )
    parser.add_argument(
        "--models", default=",".join(DEFAULT_MODELS),
        help="Comma-separated models in priority order (lite first).",
    )
    parser.add_argument(
        "--work-root", default=str(REPO_ROOT / ".workers"),
        help="Directory that receives the isolated worker copies.",
    )
    parser.add_argument("--gemini-slots", default="",
                        help="GEMINI_API_KEY slots (default: all configured).")
    parser.add_argument("--openrouter-slots", default="",
                        help="OPENROUTER_API_KEY slots (default: all configured).")
    parser.add_argument("--task-timeout", type=int, default=3600)
    parser.add_argument(
        "--retry-failed", type=int, default=0,
        help="Restart failed cells this many extra rounds (same workers/slots).",
    )
    parser.add_argument(
        "--retry-cooldown", type=int, default=60,
        help="Seconds to wait before each retry round.",
    )
    parser.add_argument(
        "--health-probe", action="store_true",
        help="Probe every configured key once (tiny request) and auto-drop "
             "slots with 401/403/429 before assigning workers.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--remove-workspaces", action="store_true",
                        help="Delete worker copies (logs included) after the run.")
    args = parser.parse_args()
    if args.runs < 1 or args.workers < 1 or args.task_timeout < 1:
        parser.error("--runs, --workers and --task-timeout must be positive")

    models = [item.strip() for item in args.models.split(",") if item.strip()]
    if not models:
        parser.error("--models must list at least one model")
    unknown = [m for m in models if model_registry.resolve_model(m) is None]
    if unknown:
        parser.error(f"unknown models: {', '.join(unknown)}")

    results_dir = Path(args.results_dir).resolve()
    names = env_names()

    # Resolve configured key slots per provider (names only, never values).
    provider_slots: Dict[str, List[int]] = {}
    for model in models:
        resolved = model_registry.resolve_model(model)
        provider = resolved[0].provider if resolved else None
        if provider is None or provider in provider_slots:
            continue
        prefix = PROVIDER_KEY_ENV.get(provider)
        if not prefix:
            provider_slots[provider] = []
            continue
        raw = {"gemini": args.gemini_slots,
               "openrouter": args.openrouter_slots}.get(provider, "")
        requested = ([int(v.strip()) for v in raw.split(",") if v.strip()]
                     if raw else available_slots(prefix, names))
        existing = [s for s in requested if s == 1 or f"{prefix}_{s}" in names]
        for slot in requested:
            if slot not in existing:
                logger.warning("Missing key %s slot %d — reported, not fatal",
                               prefix, slot)
        if not existing:
            logger.error("No %s configured — related cells will be SKIPPED", prefix)
            provider_slots[provider] = []
            continue
        if args.health_probe and PROVIDER_BASE_URL.get(provider):
            probe_model = model_registry.resolve_model(model)
            probe_id = probe_model[0].model_id if probe_model else model
            healthy, report = probe_key_health(
                prefix, existing, probe_id, PROVIDER_BASE_URL[provider])
            for line in report:
                logger.info("key-health %s: %s", prefix, line)
            provider_slots[provider] = healthy
        else:
            provider_slots[provider] = existing

    # Safely get priority_order with default value (handles case when only --task-delay is passed)
    priority_order = getattr(args, "priority_order", "simple_prompting/interface,chain_of_thought_prompting/interface")
    priority_pairs = []
    for pair in priority_order.split(","):
        pair = pair.strip()
        if "/" in pair:
            s, c = pair.split("/", 1)
            priority_pairs.append((s, c))

    pending = missing_tasks(results_dir, models, args.runs,
                            priority_order=priority_pairs if priority_pairs else None)
    logger.info("Missing cells: %d (priority: %s)",
                len(pending), " -> ".join(models))

    skipped = [t for t in pending if not provider_slots.get(t.provider or "")]
    if skipped:
        logger.error("Skipping %d cells: no API key configured", len(skipped))
    runnable = [t for t in pending if t not in skipped]
    if not runnable:
        logger.info("Nothing to run.")
        return 1 if skipped else 0


    # Each worker pins one slot per provider for its whole queue.
    worker_slots: List[Dict[str, Tuple[Optional[str], Optional[int]]]] = []
    for worker_index in range(args.workers):
        assigned: Dict[str, Tuple[Optional[str], Optional[int]]] = {}
        for provider, slots in provider_slots.items():
            prefix = PROVIDER_KEY_ENV.get(provider)
            if not prefix or not slots:
                assigned[provider] = (None, None)
                continue
            if len(slots) < args.workers:
                logger.warning("%s has %d keys for %d workers — keys are shared",
                               prefix, len(slots), args.workers)
            assigned[provider] = (prefix, slots[worker_index % len(slots)])
        worker_slots.append(assigned)

    plan = split_round_robin(runnable, args.workers)
    if args.dry_run:
        for index, worker_tasks in enumerate(plan):
            slots = ", ".join(
                f"{prefix}#{slot}"
                for prefix, slot in worker_slots[index].values() if prefix
            ) or "no keys"
            logger.info("worker w%d [%s]: %d cells", index + 1, slots,
                        len(worker_tasks))
            for task in worker_tasks:
                logger.info("  w%d -> %s", index + 1, task.label())
        if skipped:
            logger.info("skipped (no key): %d cells", len(skipped))
        return 0

    work_root = Path(args.work_root)
    work_root.mkdir(parents=True, exist_ok=True)
    workspaces = [prepare_workspace(work_root, i + 1) for i in range(args.workers)]
    logger.info("Workspaces ready under %s", work_root)

    results: List[TaskResult] = []
    current_plan = plan
    for round_index in range(args.retry_failed + 1):
        if round_index > 0:
            pending = missing_tasks(results_dir, models, args.runs)
            runnable = [t for t in pending if t not in skipped]
            if not runnable:
                logger.info("Retry round %d: nothing left to run.", round_index)
                break
            current_plan = split_round_robin(runnable, args.workers)
            logger.info("Retry round %d: %d cells after %ds cooldown",
                        round_index, len(runnable), args.retry_cooldown)
            time.sleep(args.retry_cooldown)
        if not any(current_plan):
            continue
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [
                pool.submit(run_worker, workspaces[index], results_dir,
                            worker_tasks, worker_slots[index], args.task_timeout)
                for index, worker_tasks in enumerate(current_plan) if worker_tasks
            ]
            for future in as_completed(futures):
                results.extend(future.result())

    failed = [r for r in results if not r.complete]
    logger.info("Finished: %d run, %d succeeded, %d failed, %d skipped (no key)",
                len(results), len(results) - len(failed), len(failed), len(skipped))

    for model in models:
        done = sum(
            1 for run_id in range(1, args.runs + 1)
            for strategy in STRATEGIES for context in CONTEXTS
            if is_complete(results_dir / strategy / context / model
                           / f"run_{run_id:03d}")
        )
        logger.info("Progress %s: %d/%d", model, done,
                    args.runs * len(STRATEGIES) * len(CONTEXTS))

    for result in failed:
        logger.error("Still missing: %s | %s", result.task.label(), result.reason)
    for task in skipped:
        logger.error("Key missing, not run: %s", task.label())
    logger.info("Worker logs: %s", work_root)
    if args.remove_workspaces:
        for workspace in workspaces:
            shutil.rmtree(workspace, ignore_errors=True)
        logger.info("Workspaces removed.")
    return 1 if (failed or skipped) else 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    )
    raise SystemExit(main())


