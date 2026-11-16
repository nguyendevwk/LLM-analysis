"""
CLI Experiment Runner.

This module orchestrates automated unit test generation experiments using
CLI-based LLM tools. It manages experiment execution, result storage, and
analysis pipeline integration for evaluating different prompting strategies
and code context levels across multiple models.

The runner supports:
    - Single experiment execution
    - Batch experiment processing from configuration files
    - Multi-run experiment tracking (run_001, run_002, etc.)
    - Integration with analysis pipeline (coverage, mutation testing)
    - Universal mode: Test generation for any Python class
    - Legacy mode: Backwards compatible with OrderCalculator

Usage:
    # Legacy mode (OrderCalculator)
    python cli_experiment_runner.py --model MODEL --strategy STRATEGY --context CONTEXT

    # Universal mode (any class)
    python cli_experiment_runner.py --source-file path/to/class.py --model MODEL --strategy STRATEGY --context CONTEXT

    python cli_experiment_runner.py --config config.json
    python cli_experiment_runner.py --list-models
"""

import logging
import json
import csv
import gc
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from cli_automation import (
    ClaudeCodeClient,
    GeminiCLIClient
)

import model_registry

from experiment_runner import ExperimentRunner
from prompt_strategies import SimplePrompting, ChainOfThoughtPrompting, MetamorphicPrompting
from archive_utils import create_safe_results_archive

logger = logging.getLogger(__name__)


def free_gpu_memory(verbose: bool = False):
    """
    Release cached GPU memory and run Python garbage collection.
    Helps prevent VRAM fragmentation and leaks across repeated runs.
    """
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            if hasattr(torch.cuda, "ipc_collect"):
                torch.cuda.ipc_collect()
            allocated = torch.cuda.memory_allocated() / (1024 ** 3)
            reserved = torch.cuda.memory_reserved() / (1024 ** 3)
            if verbose:
                msg = f"[VRAM Status] GPU memory released: Allocated={allocated:.2f}GB, Reserved={reserved:.2f}GB"
                logger.info(msg)
                print(msg)
    except ImportError:
        pass


METRIC_SPECS = [
    ("statement_coverage", "Statement Coverage", "%"),
    ("branch_coverage", "Branch Coverage", "%"),
    ("mutation_score", "Mutation Score", "%"),
    ("test_success_rate", "Test Success Rate", "%"),
    ("method_coverage_rate", "Method Coverage Rate", "%"),
    ("overall_quality_score", "Overall Quality Score", "%"),
    ("total_assertions", "Total Assertions", "count"),
    ("avg_assertions_per_test", "Avg Assertions / Test", "ratio"),
    ("tests_generated", "Tests Generated", "count"),
    ("tests_passed", "Tests Passed", "count"),
    ("tests_failed", "Tests Failed", "count"),
    ("mutants_killed", "Mutants Killed", "count"),
    ("total_mutants", "Total Mutants", "count"),
    ("response_time", "Response Time", "s"),
]


class CLIExperimentRunner:
    """
    Orchestrates CLI-based LLM experiments for test generation.

    Supports two modes:
    - Legacy mode (extractor=None): Uses OrderCalculator defaults
    - Universal mode (extractor provided): Uses any Python class
    """

    def __init__(
        self,
        base_results_dir="cli_results_v1",
        run_id=None,
        extractor=None,
        temperature=None,
        max_tokens=None,
        api_key=None,
        self_debug: bool = False,
        self_debug_rounds: int = 1,
    ):
        """
        Initialize the CLI experiment runner.

        Args:
            base_results_dir: Directory for storing results
            run_id: Run identifier (number, "overwrite", or None for auto-increment)
            extractor: ClassContextExtractor for universal mode (None for legacy)
            temperature: Sampling temperature for API providers (optional)
            max_tokens: Max completion tokens limit (optional)
            api_key: Override API key for this runner instance (optional)
            self_debug: Enable Execution-Guided Self-Debugging loop using traceback feedback
            self_debug_rounds: Max reflection/debugging iterations when tests fail (default: 1)
        """
        self.base_results_dir = Path(base_results_dir)
        self.base_results_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.extractor = extractor
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.self_debug = bool(self_debug)
        self.self_debug_rounds = max(1, int(self_debug_rounds))

        self.client_kwargs = {}
        if temperature is not None:
            self.client_kwargs["temperature"] = temperature
        if max_tokens is not None:
            self.client_kwargs["max_tokens"] = max_tokens
        if api_key is not None:
            self.client_kwargs["api_key"] = api_key

        self.cli_clients = {
            # Claude Code models (newest first)
            'claude-code-opus-4.5': lambda: ClaudeCodeClient(model="claude-opus-4.5"),
            'claude-code-sonnet-4.5': lambda: ClaudeCodeClient(model="claude-sonnet-4.5"),
            'claude-code-opus-4.1': lambda: ClaudeCodeClient(model="claude-opus-4.1"),

            # Gemini CLI models (newest first)
            'gemini-3-pro': lambda: GeminiCLIClient(model="gemini-3-pro-preview"),
            'gemini-3-flash': lambda: GeminiCLIClient(model="gemini-3-flash-preview"),
            'gemini-2.5-pro': lambda: GeminiCLIClient(model="gemini-2.5-pro"),
            'gemini-2.5-flash': lambda: GeminiCLIClient(model="gemini-2.5-flash"),
        }

        # Free/open providers (API-key based, no CLI tools required):
        # Gemini API, OpenRouter, Groq and local OpenAI-compatible servers.
        self.cli_clients.update(model_registry.build_client_factories(**self.client_kwargs))

        logger.info(f"CLI Experiment Runner initialized with {len(self.cli_clients)} models")
        if run_id == "overwrite":
            logger.info("Run mode: overwrite (legacy - no run numbering)")
        elif run_id is not None:
            logger.info(f"Run mode: fixed run ID = {run_id}")
        else:
            logger.info("Run mode: auto-increment run numbering")

    def _get_next_run_id(self, base_dir: Path) -> int:
        if not base_dir.exists():
            return 1

        existing_runs = []
        for item in base_dir.iterdir():
            if item.is_dir() and item.name.startswith('run_'):
                try:
                    run_num = int(item.name.replace('run_', ''))
                    existing_runs.append(run_num)
                except ValueError:
                    continue

        if not existing_runs:
            return 1

        return max(existing_runs) + 1

    def _get_result_dir(self, strategy_name: str, context_type: str, model_name: str) -> Path:
        base_path = self.base_results_dir / strategy_name / context_type / model_name

        if self.run_id == "overwrite":
            return base_path

        if self.run_id is None:
            next_run = self._get_next_run_id(base_path)
            run_dir = base_path / f"run_{next_run:03d}"
            logger.info(f"Using auto-incremented run: run_{next_run:03d}")
            return run_dir

        run_dir = base_path / f"run_{self.run_id:03d}"
        logger.info(f"Using specified run: run_{self.run_id:03d}")
        return run_dir

    def _resolve_model_name(self, model_name: str) -> str:
        """Resolve model name and register ad-hoc providers if necessary."""
        resolved = model_registry.resolve_model(model_name)
        if resolved is not None:
            spec, canonical = resolved
            if canonical not in self.cli_clients:
                self.cli_clients[canonical] = model_registry.make_client_factory(
                    spec, **self.client_kwargs
                )
                logger.info(
                    "Registered ad-hoc model %s (%s/%s)",
                    canonical, spec.provider, spec.model_id
                )
            return canonical
        elif model_name not in self.cli_clients:
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Available models: {', '.join(self.cli_clients.keys())}. "
                f"Ad-hoc syntax: openrouter:org/model | groq:model-id | "
                f"gemini:model-id | local:model-id | hf:repo-id"
            )
        return model_name

    def run_single_experiment(
        self,
        model_name: str,
        strategy_name: str,
        context_type: str,
        existing_client: Optional[Any] = None,
        custom_run_dir: Optional[Path] = None,
    ) -> Optional[dict]:
        logger.info(f"Starting CLI experiment: {model_name} - {strategy_name} - {context_type}")

        model_name = self._resolve_model_name(model_name)

        if custom_run_dir is not None:
            result_dir = Path(custom_run_dir)
        else:
            result_dir = self._get_result_dir(strategy_name, context_type, model_name)
        result_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Results will be saved to: {result_dir}")

        client = None
        should_close = False
        try:
            if existing_client is not None:
                client = existing_client
                should_close = False
            else:
                client_factory = self.cli_clients[model_name]
                client = client_factory()
                if hasattr(client, "__enter__"):
                    client = client.__enter__()
                should_close = True

            logger.info(f"Initialized client: {client}")

            # Create strategy with extractor for universal mode
            if strategy_name == "simple_prompting":
                strategy = SimplePrompting(extractor=self.extractor)
            elif strategy_name == "chain_of_thought_prompting":
                strategy = ChainOfThoughtPrompting(extractor=self.extractor)
            elif strategy_name == "metamorphic_prompting":
                strategy = MetamorphicPrompting(extractor=self.extractor)
            else:
                raise ValueError(f"Unknown strategy: {strategy_name}")

            logger.info(f"Executing {strategy_name} strategy...")
            strategy_result = strategy.execute(client, context_type)

            if not strategy_result:
                logger.error("Strategy execution failed")
                return None

            # Create analysis runner with extractor for universal mode
            analysis_runner = ExperimentRunner(extractor=self.extractor)

            experiment_data = analysis_runner.save_experiment_results(
                result_dir,
                strategy_result,
                model_name,
                strategy_name,
                context_type
            )

            if not experiment_data:
                logger.error("Failed to save experiment results")
                return None

            if self.self_debug and client is not None:
                self._run_self_debugging_loop(
                    client=client,
                    result_dir=result_dir,
                    analysis_runner=analysis_runner,
                    experiment_data=experiment_data
                )

            logger.info("Running analysis pipeline...")
            analysis_results = analysis_runner.run_analysis(result_dir, experiment_data)

            logger.info("Experiment completed successfully")
            logger.info("Results saved to: %s", result_dir)

            # Update statistical summary across all completed runs in setting_dir
            try:
                setting_dir = result_dir.parent
                all_setting_runs = []
                for item in sorted(setting_dir.iterdir()):
                    if item.is_dir() and item.name.startswith("run_"):
                        analysis_json = item / "analysis_results.json"
                        if analysis_json.exists():
                            try:
                                with open(analysis_json, "r", encoding="utf-8") as f:
                                    data = json.load(f)
                                    if data.get("summary"):
                                        all_setting_runs.append({
                                            "run_id": item.name,
                                            "result_dir": str(item),
                                            "summary": data["summary"],
                                        })
                            except Exception:
                                pass
                if all_setting_runs:
                    self._compute_and_save_statistical_summary(
                        setting_dir, model_name, strategy_name, context_type, all_setting_runs
                    )
            except Exception as ex:
                logger.debug(f"Could not update statistical summary for single run: {ex}")

            return {
                'experiment': experiment_data,
                'analysis': analysis_results,
                'result_dir': str(result_dir)
            }

        except Exception as e:
            logger.error(f"Experiment failed: {e}", exc_info=True)
            return None
        finally:
            if should_close and client is not None:
                if hasattr(client, "__exit__"):
                    try:
                        client.__exit__(None, None, None)
                    except Exception:
                        pass
                elif hasattr(client, "close"):
                    try:
                        client.close()
                    except Exception:
                        pass
                del client
                free_gpu_memory(verbose=False)

    def _run_self_debugging_loop(
        self,
        client: Any,
        result_dir: Path,
        analysis_runner: ExperimentRunner,
        experiment_data: dict,
    ) -> dict:
        """
        Execution-Guided Self-Debugging Loop (Traceback Feedback).

        If generated tests fail or error at runtime, this loop executes the suite,
        captures the exact Python unittest traceback, feeds it back to the LLM
        with targeted repair instructions, and verifies the repaired suite.
        """
        tests_file = result_dir / "tests.py"
        if not tests_file.exists():
            return {}

        initial_comp = analysis_runner.test_compilation_and_execution(tests_file)
        if initial_comp.get("execution_success") and initial_comp.get("tests_failed", 0) == 0:
            logger.info("[Self-Debugging] Initial test suite passed completely (100% pass rate). No repair needed.")
            return {
                "needed": False,
                "repaired": False,
                "initial_passed": initial_comp.get("tests_passed", 0),
                "initial_failed": 0
            }

        logger.info(
            f"[Self-Debugging] Test execution failures detected: "
            f"{initial_comp.get('tests_passed', 0)} passed, {initial_comp.get('tests_failed', 0)} failed. "
            f"Starting self-debugging loop (max {self.self_debug_rounds} rounds)..."
        )

        source_file = result_dir / f"{analysis_runner.module_name}.py"
        source_code = source_file.read_text(encoding="utf-8") if source_file.exists() else ""

        current_comp = initial_comp
        best_code = tests_file.read_text(encoding="utf-8")
        rounds_applied = 0

        for round_idx in range(1, self.self_debug_rounds + 1):
            rounds_applied += 1
            error_output = current_comp.get("raw_execution_output") or "\n".join(current_comp.get("compilation_errors", []))
            current_test_code = tests_file.read_text(encoding="utf-8")

            prompt = (
                f"The generated Python unit test suite for `{analysis_runner.class_name}` encountered execution failures during testing.\n\n"
                f"### Source Code of `{analysis_runner.class_name}`:\n"
                f"```python\n{source_code.strip()}\n```\n\n"
                f"### Current Unit Test Suite:\n"
                f"```python\n{current_test_code.strip()}\n```\n\n"
                f"### Unittest Failure Output & Traceback:\n"
                f"```\n{error_output.strip()}\n```\n\n"
                f"### Repair Instructions:\n"
                f"Carefully analyze each failure in the traceback and compare it to the class implementation:\n"
                f"1. Precondition Errors: Methods like `get_subtotal()` or `calculate_total()` raise `ValueError` on an empty cart. Add at least one item first if testing normal calculation, or verify the exception using `with self.assertRaises(ValueError):`.\n"
                f"2. Strict Assertions: Check exact formula calculations, threshold values, and return values matching the source implementation.\n"
                f"3. Invariant / Metamorphic Relations: Ensure tests verify actual state changes (e.g., adding an item then removing it returns the cart to empty, rather than matching an intermediate state).\n"
                f"4. Do NOT remove or skip test methods. Fix the failing assertions or preconditions so that ALL test methods execute and PASS.\n\n"
                f"Output ONLY the complete, repaired Python unit test suite enclosed in ```python ... ```."
            )

            logger.info(f"[Self-Debugging] Round {round_idx}/{self.self_debug_rounds}: Sending failure traceback to model...")
            try:
                repaired_response = client.send_prompt(prompt)
            except Exception as ex:
                logger.warning(f"[Self-Debugging] Round {round_idx} prompt failed: {ex}")
                break

            if not repaired_response:
                logger.warning(f"[Self-Debugging] Round {round_idx}: Model returned empty response.")
                break

            repaired_code = analysis_runner.extract_test_code(repaired_response)
            if not repaired_code or not repaired_code.strip():
                logger.warning(f"[Self-Debugging] Round {round_idx}: Could not extract test code from response.")
                continue

            candidate_file = result_dir / f"tests_candidate_round_{round_idx}.py"
            candidate_file.write_text(repaired_code, encoding="utf-8")

            cand_comp = analysis_runner.test_compilation_and_execution(candidate_file)

            is_better = False
            if cand_comp.get("compilation_success"):
                cand_passed = cand_comp.get("tests_passed", 0)
                cand_failed = cand_comp.get("tests_failed", 0)
                curr_passed = current_comp.get("tests_passed", 0)
                curr_failed = current_comp.get("tests_failed", 0)

                if cand_comp.get("execution_success") and cand_failed == 0:
                    is_better = True
                elif cand_failed < curr_failed:
                    is_better = True
                elif cand_passed > curr_passed and cand_failed <= curr_failed:
                    is_better = True

            if is_better:
                logger.info(
                    f"[Self-Debugging] Round {round_idx} SUCCESS: Candidate improved test suite! "
                    f"({current_comp.get('tests_passed')} -> {cand_comp.get('tests_passed')} passed, "
                    f"{current_comp.get('tests_failed')} -> {cand_comp.get('tests_failed')} failed)"
                )
                best_code = repaired_code
                tests_file.write_text(best_code, encoding="utf-8")
                current_comp = cand_comp
                if cand_comp.get("execution_success") and cand_comp.get("tests_failed", 0) == 0:
                    logger.info("[Self-Debugging] 100% tests passed! Early stopping loop.")
                    try:
                        candidate_file.unlink(missing_ok=True)
                    except Exception:
                        pass
                    break
            else:
                logger.info(
                    f"[Self-Debugging] Round {round_idx}: Candidate did not improve suite "
                    f"({cand_comp.get('tests_passed')} passed, {cand_comp.get('tests_failed')} failed). Keeping previous version."
                )

            try:
                candidate_file.unlink(missing_ok=True)
            except Exception:
                pass

            free_gpu_memory(verbose=False)

        # Update mutmut_test.py with the repaired passing tests
        mutmut_test_file = result_dir / "mutmut_test.py"
        analysis_runner.create_filtered_test_file(tests_file, mutmut_test_file)

        # Record self-debugging telemetry in experiment_data
        self_debug_info = {
            "enabled": True,
            "rounds_configured": self.self_debug_rounds,
            "rounds_executed": rounds_applied,
            "initial_passed": initial_comp.get("tests_passed", 0),
            "initial_failed": initial_comp.get("tests_failed", 0),
            "final_passed": current_comp.get("tests_passed", 0),
            "final_failed": current_comp.get("tests_failed", 0),
            "all_passed": bool(current_comp.get("execution_success", False) and current_comp.get("tests_failed", 0) == 0),
        }
        experiment_data["self_debug"] = self_debug_info

        results_file = result_dir / "experiment_results.json"
        try:
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(experiment_data, f, indent=2, ensure_ascii=False)
        except Exception as ex:
            logger.warning(f"Failed to update experiment_results.json with self_debug telemetry: {ex}")

        return self_debug_info

    def _compute_and_save_statistical_summary(
        self,
        target_dir: Path,
        model_name: str,
        strategy_name: str,
        context_type: str,
        setting_runs: List[dict]
    ) -> dict:
        """
        Compute mean, std, min, max across runs and save JSON, CSV, MD summaries.
        """
        metrics_stats = {}
        for key, label, unit in METRIC_SPECS:
            vals = []
            for r in setting_runs:
                s = r.get('summary') or {}
                v = s.get(key)
                if v is not None:
                    try:
                        vals.append(float(v))
                    except (ValueError, TypeError):
                        pass

            if vals:
                mean_v = round(statistics.mean(vals), 2)
                std_v = round(statistics.stdev(vals), 2) if len(vals) > 1 else 0.0
                min_v = round(min(vals), 2)
                max_v = round(max(vals), 2)
            else:
                mean_v, std_v, min_v, max_v = 0.0, 0.0, 0.0, 0.0

            metrics_stats[key] = {
                'label': label,
                'unit': unit,
                'mean': mean_v,
                'std': std_v,
                'min': min_v,
                'max': max_v,
                'values': vals,
            }

        summary_data = {
            'model': model_name,
            'strategy': strategy_name,
            'context': context_type,
            'total_runs': len(setting_runs),
            'successful_runs': len([r for r in setting_runs if r.get('summary')]),
            'metrics': metrics_stats,
            'runs': setting_runs,
        }

        # 1. Save JSON
        json_file = target_dir / "statistical_summary.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, default=str)

        # 2. Save CSV
        csv_file = target_dir / "statistical_summary.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Mean", "Std", "Min", "Max", "Unit"])
            for key, label, unit in METRIC_SPECS:
                m = metrics_stats[key]
                writer.writerow([label, m['mean'], m['std'], m['min'], m['max'], unit])

        # 3. Save Markdown
        md_file = target_dir / "statistical_summary.md"
        md_lines = [
            f"# Statistical Evaluation Summary",
            f"",
            f"- **Model:** `{model_name}`",
            f"- **Prompt Strategy:** `{strategy_name}`",
            f"- **Context Level:** `{context_type}`",
            f"- **Total Executions:** {len(setting_runs)} runs",
            f"",
            f"| Metric | Mean ± Std | Min | Max | Unit |",
            f"| :--- | :--- | :--- | :--- | :--- |",
        ]
        for key, label, unit in METRIC_SPECS:
            m = metrics_stats[key]
            unit_suffix = "%" if unit == "%" else ("s" if unit == "s" else "")
            mean_std_str = f"{m['mean']} ± {m['std']}{unit_suffix}"
            md_lines.append(f"| {label} | {mean_std_str} | {m['min']}{unit_suffix} | {m['max']}{unit_suffix} | {unit} |")

        md_lines.extend([
            f"",
            f"### Per-Run Detail",
            f"",
            f"| Run ID | Statement Cov (%) | Branch Cov (%) | Mutation Score (%) | Test Pass Rate (%) | Tests (Pass/Total) | Mutants Killed | Response Time |",
            f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ])
        for r in setting_runs:
            s = r.get('summary') or {}
            run_id = r.get('run_id', 'unknown')
            st_cov = s.get('statement_coverage', 0)
            br_cov = s.get('branch_coverage', 0)
            mut_score = s.get('mutation_score', 0)
            pass_rate = s.get('test_success_rate', 0)
            tests_run = s.get('tests_generated', 0)
            tests_passed = s.get('tests_passed', 0)
            mut_killed = s.get('mutants_killed', 0)
            total_mut = s.get('total_mutants', 0)
            resp_time = s.get('response_time', 0)
            md_lines.append(
                f"| `{run_id}` | {st_cov}% | {br_cov}% | {mut_score}% | {pass_rate}% | "
                f"{tests_passed}/{tests_run} | {mut_killed}/{total_mut} | {resp_time:.2f}s |"
            )

        md_lines.append("")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))

        logger.info(f"Statistical summaries saved in {target_dir}")
        return summary_data

    def _generate_cross_context_comparison(
        self,
        target_dir: Path,
        model_name: str,
        strategy_name: str,
        context_results: Dict[str, dict]
    ) -> dict:
        """
        Generate cross-context comparison table (JSON, CSV, MD) across context levels.
        """
        contexts = list(context_results.keys())
        comparison_data = {
            'model': model_name,
            'strategy': strategy_name,
            'contexts': contexts,
            'metrics': {},
        }

        for key, label, unit in METRIC_SPECS:
            comparison_data['metrics'][key] = {
                'label': label,
                'unit': unit,
                'contexts': {
                    ctx: context_results[ctx]['metrics'][key]
                    for ctx in contexts
                    if key in context_results[ctx].get('metrics', {})
                }
            }

        # 1. JSON
        json_file = target_dir / "cross_context_summary.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_data, f, indent=2, default=str)

        # 2. CSV
        csv_file = target_dir / "cross_context_summary.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            header = ["Metric", "Unit"]
            for ctx in contexts:
                header.extend([f"{ctx}_mean", f"{ctx}_std"])
            writer.writerow(header)

            for key, label, unit in METRIC_SPECS:
                row = [label, unit]
                for ctx in contexts:
                    m = context_results[ctx]['metrics'].get(key, {})
                    row.extend([m.get('mean', 0.0), m.get('std', 0.0)])
                writer.writerow(row)

        # 3. Markdown
        md_file = target_dir / "cross_context_summary.md"
        md_lines = [
            f"# Cross-Context Comparison Report",
            f"",
            f"- **Model:** `{model_name}`",
            f"- **Prompt Strategy:** `{strategy_name}`",
            f"- **Evaluated Contexts:** {', '.join([f'`{c}`' for c in contexts])}",
            f"",
            f"| Metric | " + " | ".join([f"{ctx}" for ctx in contexts]) + " |",
            f"| :--- | " + " | ".join([":---" for _ in contexts]) + " |",
        ]
        for key, label, unit in METRIC_SPECS:
            unit_suffix = "%" if unit == "%" else ("s" if unit == "s" else "")
            cells = []
            for ctx in contexts:
                m = context_results[ctx]['metrics'].get(key, {})
                mean_v = m.get('mean', 0.0)
                std_v = m.get('std', 0.0)
                cells.append(f"{mean_v} ± {std_v}{unit_suffix}")
            md_lines.append(f"| {label} | " + " | ".join(cells) + " |")

        md_lines.append("")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))

        logger.info(f"Cross-context comparison saved to {target_dir}")
        return comparison_data

    def run_matrix_with_statistics(
        self,
        model_name: str,
        strategies: List[str],
        contexts: List[str],
        runs_per_setting: int = 1,
    ) -> Dict[str, Any]:
        """
        Execute experiments across strategies and contexts with N runs per setting.
        Reuses client across runs, empties CUDA cache between iterations,
        and guarantees complete VRAM unloading upon completion.
        """
        model_name = self._resolve_model_name(model_name)
        client = None
        all_results = {}

        try:
            client_factory = self.cli_clients[model_name]
            client = client_factory()
            if hasattr(client, "__enter__"):
                client = client.__enter__()

            total_settings = len(strategies) * len(contexts)
            total_runs = total_settings * runs_per_setting
            current_run = 0

            logger.info(
                f"\n{'='*70}\n"
                f"Starting Matrix Experiment Suite:\n"
                f"  Model: {model_name}\n"
                f"  Strategies ({len(strategies)}): {', '.join(strategies)}\n"
                f"  Contexts ({len(contexts)}): {', '.join(contexts)}\n"
                f"  Runs per setting: {runs_per_setting}\n"
                f"  Total runs to execute: {total_runs}\n"
                f"{'='*70}\n"
            )

            for strat_idx, strategy in enumerate(strategies, 1):
                all_results[strategy] = {}
                for ctx_idx, context in enumerate(contexts, 1):
                    setting_dir = self.base_results_dir / strategy / context / model_name
                    setting_dir.mkdir(parents=True, exist_ok=True)
                    setting_runs = []

                    start_run = self._get_next_run_id(setting_dir) if self.run_id != "overwrite" else 1

                    for run_offset in range(runs_per_setting):
                        run_idx = start_run + run_offset
                        current_run += 1
                        run_dir = setting_dir / f"run_{run_idx:03d}"
                        logger.info(
                            f"\n[{current_run}/{total_runs}] Running: "
                            f"{strategy} | {context} | {model_name} | run_{run_idx:03d}"
                        )

                        res = self.run_single_experiment(
                            model_name=model_name,
                            strategy_name=strategy,
                            context_type=context,
                            existing_client=client,
                            custom_run_dir=run_dir,
                        )

                        if res and res.get('analysis') and res['analysis'].get('summary'):
                            setting_runs.append({
                                'run_idx': run_idx,
                                'run_id': f"run_{run_idx:03d}",
                                'result_dir': str(run_dir),
                                'summary': res['analysis']['summary'],
                            })
                        else:
                            logger.warning(f"Run {run_idx} for {strategy}/{context} produced no summary.")

                        # Clear intermediate generation tensors and garbage collect
                        free_gpu_memory(verbose=False)

                    # Collect all runs in setting_dir with valid analysis for complete statistical aggregation
                    all_setting_runs = []
                    for item in sorted(setting_dir.iterdir()):
                        if item.is_dir() and item.name.startswith("run_"):
                            analysis_json = item / "analysis_results.json"
                            if analysis_json.exists():
                                try:
                                    with open(analysis_json, "r", encoding="utf-8") as f:
                                        data = json.load(f)
                                        if data.get("summary"):
                                            all_setting_runs.append({
                                                "run_id": item.name,
                                                "result_dir": str(item),
                                                "summary": data["summary"],
                                            })
                                except Exception:
                                    pass

                    runs_to_summarize = all_setting_runs if all_setting_runs else setting_runs
                    if runs_to_summarize:
                        stat_summary = self._compute_and_save_statistical_summary(
                            setting_dir, model_name, strategy, context, runs_to_summarize
                        )
                        all_results[strategy][context] = stat_summary

                # If multiple contexts were executed for this strategy, generate cross-context comparison
                if len(contexts) > 1 and all_results[strategy]:
                    cross_dir = self.base_results_dir / strategy / model_name
                    cross_dir.mkdir(parents=True, exist_ok=True)
                    self._generate_cross_context_comparison(
                        cross_dir, model_name, strategy, all_results[strategy]
                    )

        finally:
            # Complete teardown and VRAM release
            if client is not None:
                if hasattr(client, "__exit__"):
                    try:
                        client.__exit__(None, None, None)
                    except Exception:
                        pass
                elif hasattr(client, "close"):
                    try:
                        client.close()
                    except Exception:
                        pass
                del client
            free_gpu_memory(verbose=True)

        return all_results

    def run_batch_experiments(self, config_file: str) -> list:
        logger.info(f"Running batch experiments from: {config_file}")

        with open(config_file) as f:
            config = json.load(f)

        experiments = config['experiments']
        delay = config.get('delay_between_experiments', 10)

        results = []

        for i, experiment in enumerate(experiments):
            model = experiment['model']
            strategy = experiment['strategy']
            context = experiment['context']

            logger.info(f"\n{'='*60}")
            logger.info(f"Experiment {i+1}/{len(experiments)}")
            logger.info(f"Model: {model}")
            logger.info(f"Strategy: {strategy}")
            logger.info(f"Context: {context}")
            logger.info(f"{'='*60}\n")

            result = self.run_single_experiment(model, strategy, context)

            if result:
                results.append(result)
                logger.info("Experiment %d/%d completed successfully", i+1, len(experiments))
            else:
                logger.error("Experiment %d/%d failed", i+1, len(experiments))

            if i < len(experiments) - 1:
                import time
                logger.info("Waiting %ds before next experiment...", delay)
                time.sleep(delay)

        logger.info("="*60)
        logger.info("Batch completed: %d/%d experiments successful", len(results), len(experiments))
        logger.info("="*60)

        return results

    def run_full_scenario(self, model_name: str, runs_per_setting: int = 1) -> dict:
        """Run all 3 strategies and all 3 context levels for one model with multi-run statistics."""
        strategies = ['simple_prompting', 'chain_of_thought_prompting', 'metamorphic_prompting']
        contexts = ['interface', 'interface_docstring', 'full_context']
        return self.run_matrix_with_statistics(
            model_name=model_name,
            strategies=strategies,
            contexts=contexts,
            runs_per_setting=runs_per_setting,
        )

    def get_available_models(self) -> list:
        return list(self.cli_clients.keys())

    def print_available_models(self):
        print("\nAvailable Models:")
        print("="*60)

        groups = {
            'OpenAI Codex': [k for k in self.cli_clients if k.startswith('codex-')],
            'Claude Code': [k for k in self.cli_clients if k.startswith('claude-code-')],
            'GitHub Copilot': [k for k in self.cli_clients if k.startswith('copilot-')],
            'Google Gemini CLI': [k for k in self.cli_clients if k.startswith('gemini-') and not k.startswith('gemini-api-')],
        }

        # Free/open providers from the model registry (API-key based)
        for group_name, models in model_registry.grouped_models().items():
            groups[group_name] = list(models.keys())

        for tool, models in groups.items():
            if not models:
                continue
            print(f"\n{tool}:")
            for model in models:
                print(f"  - {model}")

        print("\nAd-hoc syntax (any model a provider offers, free or paid):")
        print("  - openrouter:vendor/model (e.g. openrouter:anthropic/claude-3.7-sonnet)")
        print("  - groq:model-id | gemini:model-id | local:model-id | intern-ai:model-id")
        print("\n" + "="*60)

    def check_providers(self) -> bool:
        """
        Verify API keys / connectivity for all free providers.

        Prints the status of GEMINI_API_KEY, OPENROUTER_API_KEY and
        GROQ_API_KEY (from environment or .env) and probes each provider's
        /models endpoint.

        Returns:
            True if at least one provider is ready to run
        """
        import os
        from cli_automation import APIClient, PROVIDERS
        from cli_automation.api_client import load_dotenv

        load_dotenv()

        print("\nProvider check:")
        print("=" * 60)

        ready = False
        for provider, config in PROVIDERS.items():
            key_env = config["key_env"]
            key_set = bool(os.environ.get(key_env))
            label = config["label"]

            if config["key_required"] and not key_set:
                print(f"  {label:<32} key not set ({key_env})")
                continue

            try:
                client = APIClient(provider=provider, model="__probe__")
            except Exception as e:
                print(f"  {label:<32} FAILED ({e})")
                continue

            import requests
            try:
                probe = requests.get(
                    f"{client.base_url}/models",
                    headers=client._headers(),
                    timeout=10,
                )
                auth_ok = probe.status_code == 200
                status = "ready" if auth_ok else f"HTTP {probe.status_code}"
            except requests.RequestException as e:
                auth_ok = False
                status = f"unreachable ({type(e).__name__})"

            print(f"  {label:<32} {status} ({key_env})")
            ready = ready or auth_ok

        print("=" * 60)
        if not ready:
            print("No provider ready — copy .env.example to .env and add a key.")
        return ready


ALL_STRATEGIES = ['simple_prompting', 'chain_of_thought_prompting', 'metamorphic_prompting']
ALL_CONTEXTS = ['interface', 'interface_docstring', 'full_context']

STRATEGY_MAP = {
    'simple': 'simple_prompting',
    'simple_prompting': 'simple_prompting',
    'simple-prompting': 'simple_prompting',
    'cot': 'chain_of_thought_prompting',
    'chain_of_thought': 'chain_of_thought_prompting',
    'chain_of_thought_prompting': 'chain_of_thought_prompting',
    'chain-of-thought-prompting': 'chain_of_thought_prompting',
    'metamorphic': 'metamorphic_prompting',
    'metamorphic_prompting': 'metamorphic_prompting',
    'metamorphic-prompting': 'metamorphic_prompting',
}

CONTEXT_MAP = {
    'interface': 'interface',
    'interface_only': 'interface',
    'interface-only': 'interface',
    'interface_docstring': 'interface_docstring',
    'interface-docstring': 'interface_docstring',
    'docstring': 'interface_docstring',
    'full': 'full_context',
    'full_context': 'full_context',
    'full-context': 'full_context',
}


def parse_multi_values(val: Optional[str], all_list: List[str], mapping: dict) -> List[str]:
    """Parse comma-separated values or 'all' into normalized list."""
    if not val:
        return []
    s = val.strip()
    if s.lower() == 'all':
        return list(all_list)
    items = []
    for piece in s.split(','):
        p = piece.strip().lower()
        if not p:
            continue
        mapped = mapping.get(p, p)
        if mapped not in all_list:
            raise ValueError(f"Unknown value '{piece}'. Valid options: {', '.join(all_list)} or 'all'")
        if mapped not in items:
            items.append(mapped)
    return items


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='CLI Experiment Runner with multi-run statistical support and zero VRAM leak',
        epilog='''
Run ID & Multi-run modes:
  - --runs N / --iterations N: Execute N runs per setting to calculate mean, std, min, max
  - No --run-id: Auto-increment (creates run_001, run_002, etc.)
  - --run-id N: Use specific run number (e.g., --run-id 1 creates run_001)
  - --run-id overwrite: Legacy mode, no run numbering (overwrites existing results)

Context & Strategy Multi-selection:
  - Comma-separated: --context full_context,interface,interface_docstring
  - All: --context all (or --strategy all)

Source file modes:
  - No --source-file: Legacy mode (OrderCalculator)
  - --source-file path/to/class.py: Universal mode (any Python class)
  - --source-file path/to/class.py --class-name ClassName: Specify class if multiple

Examples:
  # Multi-run statistical evaluation (5 runs of metamorphic prompting on full context)
  python cli_experiment_runner.py --model hf-qwen-2.5-coder-7b --strategy metamorphic_prompting --context full_context --runs 5

  # Multi-context comparison in a single run (cross-context statistics table)
  python cli_experiment_runner.py --model hf-qwen-2.5-coder-7b --strategy metamorphic_prompting --context all --runs 3

  # Full scenario (all 3 strategies x all 3 contexts x 3 runs = 27 runs)
  python cli_experiment_runner.py --model hf-qwen-2.5-coder-7b --full-scenario --runs 3

  # Legacy single run
  python cli_experiment_runner.py --model claude-code-sonnet-4.5 --strategy simple_prompting --context interface
  # Packaging & Archiving:
  # Results are automatically zipped into a clean archive (excluding AV false-positive patterns).
  # Package existing results without re-running:
  python cli_experiment_runner.py --archive-only --results-dir cli_results_v1

  # Create both .zip and .tar.gz archives:
  python cli_experiment_runner.py --model hf-qwen-2.5-coder-7b --strategy metamorphic_prompting --context full_context --zip-format both

  # Password-protect zip archive:
  python cli_experiment_runner.py --model hf-qwen-2.5-coder-7b --strategy metamorphic_prompting --context full_context --zip-password mypass
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--model', help='Model name')
    parser.add_argument('--strategy', type=str, default=None,
                        help='Prompting strategy (or comma-separated list, or "all")')
    parser.add_argument('--context', type=str, default=None,
                        help='Code context level (or comma-separated list, or "all")')
    parser.add_argument('--runs', '--iterations', type=int, default=1, dest='runs',
                        help='Number of runs per setting to compute statistics (default: 1)')
    parser.add_argument('--config', help='JSON config file for batch experiments')
    parser.add_argument('--full-scenario', action='store_true',
                        help='Run all 3 strategies across all three context levels for one model')
    parser.add_argument('--list-models', action='store_true',
                        help='List available models (CLI + free API providers)')
    parser.add_argument('--check-providers', action='store_true',
                        help='Verify free-provider API keys (GEMINI_API_KEY, '
                             'OPENROUTER_API_KEY, GROQ_API_KEY) and connectivity')
    parser.add_argument('--run-id', type=str, default=None,
                        help='Run identifier: number (e.g., 1), "overwrite", or omit for auto-increment')
    parser.add_argument('--results-dir', type=str, default='cli_results_v1',
                        help='Directory for storing results (default: cli_results_v1)')
    parser.add_argument('--temperature', type=float, default=None,
                        help='Sampling temperature (e.g. 0.2; 0.0 = greedy)')
    parser.add_argument('--max-tokens', type=int, default=None,
                        help='Max completion tokens (default: provider default)')
    parser.add_argument('--api-key', type=str, default=None,
                        help='Override API key for this run (bypasses .env key)')

    # Archive and Compression options
    parser.add_argument('--no-zip', action='store_true',
                        help='Disable automatic packaging of results into a safe archive')
    parser.add_argument('--zip-format', choices=['zip', 'tar.gz', 'both'], default='zip',
                        help='Archive format: "zip" (default), "tar.gz" (avoids AV heuristics), or "both"')
    parser.add_argument('--zip-password', type=str, default=None,
                        help='Optional password encryption for the zip archive')
    parser.add_argument('--zip-output', type=str, default=None,
                        help='Explicit file path for the output archive')
    parser.add_argument('--archive-only', action='store_true',
                        help='Package existing results directory into safe archive without running new experiments')

    # Universal mode arguments
    parser.add_argument('--source-file', type=str, default=None,
                        help='Path to Python source file (universal mode). If omitted, uses legacy OrderCalculator mode.')
    parser.add_argument('--class-name', type=str, default=None,
                        help='Name of the class to test (auto-detected if single class in file)')
    parser.add_argument('--legacy', action='store_true',
                        help='Force legacy mode even if --source-file is provided')

    # Self-Debugging (Direction 1: Traceback Feedback Loop)
    parser.add_argument('--self-debug', action='store_true',
                        help='Enable Execution-Guided Self-Debugging loop using traceback feedback')
    parser.add_argument('--self-debug-rounds', type=int, default=1,
                        help='Maximum reflection/debugging rounds when tests fail (default: 1)')

    args, unknown_args = parser.parse_known_args()
    if unknown_args:
        logger.warning("Ignored unrecognized arguments/text: %s", " ".join(unknown_args))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cli_automation.log'),
            logging.StreamHandler()
        ]
    )

    run_id = None
    if args.run_id is not None:
        if args.run_id.lower() == 'overwrite':
            run_id = "overwrite"
        else:
            try:
                run_id = int(args.run_id)
                if run_id < 1:
                    print("Error: --run-id must be positive integer or 'overwrite'")
                    return
            except ValueError:
                print(f"Error: Invalid --run-id '{args.run_id}'. Use integer or 'overwrite'")
                return

    # Create extractor for universal mode
    extractor = None
    if args.source_file and not args.legacy:
        try:
            from class_context_extractor import ClassContextExtractor
            source_path = Path(args.source_file)
            if not source_path.exists():
                print(f"Error: Source file not found: {args.source_file}")
                return
            extractor = ClassContextExtractor(source_path, args.class_name)
            info = extractor.get_class_info()
            print(f"\n{'='*60}")
            print(f"Universal mode: {info.name}")
            print(f"Module: {info.module_name}")
            print(f"Methods: {len(info.public_methods)}")
            print(f"Helper types: {', '.join(info.helper_types) or 'None'}")
            print(f"{'='*60}\n")
        except Exception as e:
            print(f"Error initializing class extractor: {e}")
            return
    else:
        print("\n" + "="*60)
        print("Legacy mode: OrderCalculator")
        print("="*60 + "\n")

    runner = CLIExperimentRunner(
        base_results_dir=args.results_dir,
        run_id=run_id,
        extractor=extractor,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        api_key=args.api_key,
        self_debug=args.self_debug,
        self_debug_rounds=args.self_debug_rounds,
    )

    if args.list_models:
        runner.print_available_models()
        return

    if args.check_providers:
        runner.check_providers()
        return

    if args.archive_only:
        create_safe_results_archive(
            source_dir=Path(args.results_dir),
            output_path=Path(args.zip_output) if args.zip_output else None,
            output_prefix=f"results_{args.model or 'suite'}",
            archive_format=args.zip_format,
            password=args.zip_password,
            verbose=True,
        )
        return

    experiment_executed = False
    try:
        if args.config:
            experiment_executed = True
            results = runner.run_batch_experiments(args.config)
            batch_results_file = Path("cli_batch_results.json")
            with open(batch_results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Batch results saved to: {batch_results_file}")

        elif args.full_scenario:
            if not args.model:
                parser.error('--full-scenario requires --model')

            experiment_executed = True
            results = runner.run_full_scenario(args.model, runs_per_setting=args.runs)
            scenario_results_file = Path("cli_full_scenario_results.json")
            with open(scenario_results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            logger.info("Full scenario results saved to: %s", scenario_results_file)
            print(
                f"\nFull scenario completed successfully.\n"
                f"Results and cross-context reports saved under: {args.results_dir}\n"
            )

        elif args.model and args.strategy and args.context:
            try:
                strategies = parse_multi_values(args.strategy, ALL_STRATEGIES, STRATEGY_MAP)
                contexts = parse_multi_values(args.context, ALL_CONTEXTS, CONTEXT_MAP)
            except ValueError as err:
                print(f"Error: {err}")
                return

            experiment_executed = True
            if args.runs > 1 or len(strategies) > 1 or len(contexts) > 1:
                results = runner.run_matrix_with_statistics(
                    model_name=args.model,
                    strategies=strategies,
                    contexts=contexts,
                    runs_per_setting=args.runs,
                )
                print("\n" + "="*60)
                print(f"Matrix experiment completed ({len(strategies)} strategies, {len(contexts)} contexts, {args.runs} runs each).")
                print(f"Detailed statistics and cross-context tables saved under: {args.results_dir}")
                print("="*60 + "\n")
            else:
                result = runner.run_single_experiment(
                    args.model,
                    strategies[0],
                    contexts[0]
                )

                if result:
                    print("\n" + "="*60)
                    print("Experiment completed successfully")
                    print(f"Results saved to: {result['result_dir']}")
                    print("="*60 + "\n")
                else:
                    print("\n" + "="*60)
                    print("Experiment failed")
                    print("="*60 + "\n")

        else:
            parser.print_help()

        # Automatically package results into a clean archive (filtered against AV false-positives)
        if experiment_executed and not args.no_zip:
            create_safe_results_archive(
                source_dir=Path(args.results_dir),
                output_path=Path(args.zip_output) if args.zip_output else None,
                output_prefix=f"results_{args.model or 'suite'}",
                archive_format=args.zip_format,
                password=args.zip_password,
                verbose=True,
            )

    finally:
        free_gpu_memory(verbose=True)


if __name__ == "__main__":
    main()
