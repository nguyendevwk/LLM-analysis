# LLM Test Generation Analysis

Experimental framework for evaluating automated unit test generation by Large Language Models. Part of an engineering thesis: *"Impact of Code Context and Prompting Strategies on Automated Unit Test Generation with Modern Large Language Models"*.

## Overview

This system automates 720 experiments comparing 4 LLM models across 2 prompting strategies and 3 code context levels. Each experiment generates a unit test suite for the `OrderCalculator` class, then evaluates it using code coverage, mutation testing, and quality metrics.

### Models Tested (via CLI tools)

| CLI Tool     | Model              | Alias                    |
|-------------|--------------------|--------------------------|
| Claude Code  | Claude Sonnet 4.5  | `claude-code-sonnet-4.5` |
| Claude Code  | Claude Opus 4.5    | `claude-code-opus-4.5`   |
| Gemini CLI   | Gemini 3 Pro       | `gemini-3-pro`           |
| Gemini CLI   | Gemini 3 Flash     | `gemini-3-flash`         |

### Models for Replication (free providers, API key only)

| Provider    | Examples                                                              | Key env var           |
|-------------|-----------------------------------------------------------------------|-----------------------|
| Gemini API  | `gemini-api-3.8-flash`, `gemini-api-3.7-flash`, `gemini-api-3.5-flash`  | `GEMINI_API_KEY`      |
| Groq        | `groq-gpt-oss-120b`, `groq-gpt-oss-20b`, `groq-qwen3.8-27b`           | `GROQ_API_KEY`        |
| OpenRouter  | `openrouter-gemma-4-31b-it`, `openrouter-nemotron-3-super-120b-a12b`  | `OPENROUTER_API_KEY`  |
| Local       | `local-llama-3.1-8b` (Ollama/LM Studio/vLLM)                          | optional              |

Full list: `uv run python cli_experiment_runner.py --list-models` — any other
model can be addressed ad-hoc, e.g. `--model "openrouter:org/model:free"`.

### Prompting Strategies

- **Simple Prompting** -- single prompt requesting a complete test suite
- **Chain-of-Thought (CoT)** -- 3-step process: analyze, plan, implement

### Code Context Levels

- **Interface** -- method signatures only
- **Interface + Docstring** -- signatures with documentation
- **Full Context** -- complete source code

## Repository Structure

```
LLM-analysis/
├── order_calculator.py                # Class under test
├── pyproject.toml / uv.lock           # uv project (dependencies, Python pin)
├── .env.example                       # API key template (copy to .env)
├── automation/
│   ├── cli_automation/                # LLM client implementations
│   │   ├── base_cli_client.py         # Abstract base (subprocess, retry, CoT)
│   │   ├── api_client.py              # Free providers: OpenRouter/Groq/Gemini API
│   │   ├── claude_code_client.py      # Claude Code CLI client
│   │   └── gemini_cli_client.py       # Gemini CLI client
│   ├── model_registry.py              # Free/open model catalog + name resolution
│   ├── configs/                       # Batch experiment configs (JSON)
│   ├── data/                          # Aggregated experiment data
│   │   ├── raw_data.csv               # 720 experiment results
│   │   └── summary_by_config.csv      # Per-configuration summary
│   ├── cli_results/                   # Raw results (720 experiment directories)
│   │   ├── simple_prompting/
│   │   └── chain_of_thought_prompting/
│   ├── cli_experiment_runner.py       # Experiment orchestrator
│   ├── generate_batch_config.py       # Batch matrix generator
│   ├── experiment_runner.py           # Analysis pipeline
│   ├── class_context_extractor.py     # AST-based context extraction
│   ├── prompt_strategies.py           # Prompting strategy implementations
│   ├── prompt_templates.py            # Prompt template manager
│   └── streamlit_app.py              # Web interface
└── mutants/                           # Mutation testing configuration (mutmut)
```

## Architecture

### Experiment Pipeline

```
LLM Client (Claude/Gemini CLI or free API provider)
    → sends prompt (strategy + context level)
    → receives generated test code
    ↓
ExperimentRunner
    → saves test file
    → compilation check (py_compile)
    → test execution (unittest)
    → coverage analysis (coverage.py, branch mode)
    → mutation testing (mutmut, 217 mutants)
    → quality metrics (assertions, naming, independence)
    → saves analysis_results.json
```

### Universal Mode

The system supports testing any Python class via `ClassContextExtractor`, which uses AST parsing to extract class information at different context levels.

## Usage

### Requirements

- [uv](https://docs.astral.sh/uv/) — manages Python (3.10–3.12) and all dependencies
  (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- For the free providers: one API key (Gemini / OpenRouter / Groq) — see below
- Optional, for the original CLI-based models:
  [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code),
  [Gemini CLI](https://github.com/google-gemini/gemini-cli)

```bash
uv sync
```

## Reproducing on Free Providers (API key only)

Experiments can run against free, OpenAI-compatible providers — no CLI
tools required. Only a key in `.env` is needed:

1. Copy the template and fill in **one** (or more) keys:

   ```bash
   cp .env.example .env
   # GEMINI_API_KEY    — Gemini API free tier (https://aistudio.google.com/apikey)
   # OPENROUTER_API_KEY — OpenRouter free ':free' models (https://openrouter.ai/keys)
   # GROQ_API_KEY      — Groq free developer tier (https://console.groq.com/keys)
   ```

2. Verify the keys and list the available models:

   ```bash
   cd automation
   uv run python cli_experiment_runner.py --check-providers
   uv run python cli_experiment_runner.py --list-models
   ```

3. Run a single experiment:

   ```bash
   cd automation
   uv run python cli_experiment_runner.py \
     --model openrouter-gemma-4-31b-it \
     --strategy simple_prompting \
     --context full_context
   ```

4. Any model a provider offers can be used ad-hoc (the results directory
   name is derived automatically):

   ```bash
   cd automation
   uv run python cli_experiment_runner.py \
     --model "groq:openai/gpt-oss-120b" \
     --strategy chain_of_thought_prompting \
     --context interface
   ```

5. Full replication matrix (models × 2 strategies × 3 context levels × N runs):

   ```bash
   cd automation
   uv run python generate_batch_config.py \
     --models gemini-api-3.8-flash openrouter-gemma-4-31b-it groq-gpt-oss-120b \
     --runs 3 \
     --out configs/replication_free_providers.json
   uv run python cli_experiment_runner.py --config configs/replication_free_providers.json
   ```

6. Run the complete scenario for one model in a single command (2 strategies ×
   3 context levels):

   ```bash
   cd automation
   uv run python cli_experiment_runner.py \
     --model gemini-api-3.8-flash \
     --full-scenario
   ```

   The six experiment results are saved to `cli_full_scenario_results.json`.

Curated free models live in `automation/model_registry.py` (add one line to
extend). Local open-weight servers (Ollama / LM Studio / vLLM) work through
the `local` provider and `LOCAL_BASE_URL`. Request settings can be tuned via
`LLM_TEMPERATURE`, `LLM_MAX_TOKENS`, `LLM_TIMEOUT` and `LLM_MAX_RETRIES`.

### Run Single Experiment

```bash
cd automation
uv run python cli_experiment_runner.py \
  --model claude-code-sonnet-4.5 \
  --strategy simple_prompting \
  --context full_context
```

### Run with Custom Class (Universal Mode)

```bash
cd automation
uv run python cli_experiment_runner.py \
  --source-file path/to/my_class.py \
  --model gemini-3-pro \
  --strategy chain_of_thought_prompting \
  --context interface_docstring
```

### Web Interface

```bash
cd automation
uv run streamlit run streamlit_app.py
```

In the web interface, enable **Run full scenario** to run all six
strategy/context combinations for the selected model and view the results in
one table.

### Key Results (720 experiments)

| Model              | Statement Coverage | Branch Coverage | Mutation Score |
|--------------------|--------------------|-----------------|----------------|
| Claude Sonnet 4.5  | 93.7%              | 91.4%           | 35.5%          |
| Claude Opus 4.5    | 93.6%              | 91.1%           | 36.0%          |
| Gemini 3 Flash     | 89.3%              | 87.4%           | 25.0%          |
| Gemini 3 Pro       | 88.8%              | 85.3%           | 26.1%          |

Context level impact on statement coverage: Interface (79.3%) -> Interface+Docstring (96.4%) -> Full Context (98.4%)

## Notes

- Setup is fully managed by `uv` (`pyproject.toml` + `uv.lock`); Python is pinned to 3.10–3.12 because the mutation pipeline uses mutmut 2.x
- Free-provider requests retry automatically with backoff on rate limits (429)
- Mutation testing requires `fork()` support (Linux/WSL only, not native Windows)
- All 720 experiments are stored in `automation/cli_results/`
- Aggregated data is available in `automation/data/`



  curl https://openrouter.ai/api/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer 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" \
    -d '{
    "model": "nvidia/nemotron-3.5-lightning:free",
    "messages": [
      {
        "role": "user",
        "content": "How many r`s are in the word `strawberry?`"
      }
    ],
    "reasoning": {
      "enabled": true
    }
}'
