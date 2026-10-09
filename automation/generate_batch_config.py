"""
Batch Experiment Config Generator.

Generates a JSON config for cli_experiment_runner.py covering the full
experiment matrix:

    models × strategies × context levels × runs

Example (replication on free providers):

    # Full matrix for 3 models, 3 runs each = 3 × 2 × 3 × 3 = 54 experiments
    python generate_batch_config.py \
        --models gemini-api-3.8-flash openrouter-gemma-4-31b-it groq-gpt-oss-120b \
        --runs 3 \
        --out configs/replication_open_providers.json

Run it with:

    python cli_experiment_runner.py --config configs/replication_open_providers.json
"""

import argparse
import json
from pathlib import Path

STRATEGIES = ["simple_prompting", "chain_of_thought_prompting"]
CONTEXTS = ["interface", "interface_docstring", "full_context"]


def generate(models, runs: int, delay: int) -> dict:
    """Build the batch config dictionary."""
    experiments = []
    for model in models:
        for _ in range(runs):
            for strategy in STRATEGIES:
                for context in CONTEXTS:
                    experiments.append({
                        "model": model,
                        "strategy": strategy,
                        "context": context,
                    })

    return {
        "description": (
            "Auto-generated experiment matrix: "
            f"{len(models)} models × {len(STRATEGIES)} strategies × "
            f"{len(CONTEXTS)} contexts × {runs} runs"
        ),
        "delay_between_experiments": delay,
        "experiments": experiments,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate a batch experiment config (JSON)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Available model names: python cli_experiment_runner.py --list-models\n"
            "Ad-hoc syntax also works: openrouter:org/model:free | groq:model-id"
        ),
    )
    parser.add_argument(
        "--models", nargs="+", required=True,
        help="Model names as accepted by --model",
    )
    parser.add_argument(
        "--runs", type=int, default=1,
        help="Repetitions per model (run_001, run_002, ...) (default: 1)",
    )
    parser.add_argument(
        "--delay", type=int, default=15,
        help="Seconds to wait between experiments (default: 15, free tiers "
             "are rate-limited)",
    )
    parser.add_argument(
        "--out", type=str, default="configs/generated_batch.json",
        help="Output JSON path (default: configs/generated_batch.json)",
    )
    args = parser.parse_args()

    config = generate(args.models, args.runs, args.delay)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    print(f"Config written to {out_path}")
    print(f"Experiments: {len(config['experiments'])}")


if __name__ == "__main__":
    main()
