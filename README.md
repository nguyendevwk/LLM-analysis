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
│   ├── cli_results_v3/                # Baseline 720 experiments (Claude Opus/Sonnet 4.5, Gemini 3 Flash/Pro)
│   ├── cli_results_v1/                # Open-source runs (Nemotron 3 Super 120B)
│   ├── cli_results_v10/               # Open-source runs (Groq GPT-OSS 120B)
│   ├── cli_results_v11/               # Compact model runs (Groq GPT-OSS 20B)
│   ├── synthesis_output/              # Multi-panel charts, CSV metrics & docx/slide markdown
│   ├── docs/                          # Presentation PPTX and Paper DOCX deliverables
│   ├── tools/                         # Automated report metric injectors & aggregators
│   ├── generate_synthesis_report.py   # Synthesis & multi-panel chart generation pipeline
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

### OpenRouter Models (Free & Paid/Commercial)

Both free and commercial paid models on OpenRouter are fully supported using `OPENROUTER_API_KEY` in `.env`:
- **Curated Paid / Commercial Models**:
  - **Anthropic**: `openrouter-claude-3.7-sonnet`, `openrouter-claude-3.7-sonnet-thinking`, `openrouter-claude-3.5-sonnet`, `openrouter-claude-3.5-haiku`, `openrouter-claude-3-opus`
  - **OpenAI**: `openrouter-gpt-4o`, `openrouter-gpt-4o-mini`, `openrouter-gpt-4.5-preview`, `openrouter-o3-mini`, `openrouter-o1`
  - **DeepSeek**: `openrouter-deepseek-v3`, `openrouter-deepseek-r1`
  - **Coding & Open Weights**: `openrouter-qwen-2.5-coder-32b-instruct`, `openrouter-codestral`, `openrouter-llama-3.3-70b-instruct`, `openrouter-gemini-2.0-flash`
- **Ad-hoc Syntax (Any Model)**:
  Run any model hosted on OpenRouter using `openrouter:vendor/model-name` or direct `vendor/model-name`:
  ```bash
  cd automation
  # Single run with Claude 3.7 Sonnet
  uv run python cli_experiment_runner.py --model openrouter:anthropic/claude-3.7-sonnet --strategy simple_prompting --context full_context

  # Full 6-scenario batch with GPT-4o
  uv run python cli_experiment_runner.py --model openrouter:openai/gpt-4o --full-scenario
  ```
- **Streamlit Web UI**:
  - Chế độ chọn Model: Hỗ trợ 2 chế độ linh hoạt:
    - `📋 Chọn từ danh sách`: Chọn nhanh các model curated từ Claude Code, Gemini, Groq, OpenRouter (Paid & Free), InternAI.
    - `✏️ Tự điền mã Model (Custom)`: Nhập trực tiếp bất kỳ model ID/slug nào từ [openrouter.ai/models](https://openrouter.ai/models), Groq, Gemini hoặc local server. Hệ thống tự động phân giải và tạo thư mục kết quả canonical.
  - Parameter Tuning & Override: Tùy chỉnh trực tiếp `Temperature` (slider), `Max Completion Tokens`, và `API Key Override` ngay trên giao diện web hoặc CLI flags (`--temperature`, `--max-tokens`, `--api-key`).

Curated models live in `automation/model_registry.py` (add one line to
extend). Local open-weight servers (Ollama / LM Studio / vLLM) work through
the `local` provider and `LOCAL_BASE_URL`. Request settings can be tuned via
CLI arguments (`--temperature`, `--max-tokens`, `--api-key`) or environment
variables `LLM_TEMPERATURE`, `LLM_MAX_TOKENS`, `LLM_RECOVERY_MAX_TOKENS`,
`LLM_TIMEOUT` and `LLM_MAX_RETRIES`. `LLM_MAX_TOKENS` is not set by default:
the client omits `max_tokens` and lets the provider choose the completion
limit. `LLM_RECOVERY_MAX_TOKENS` controls the retry used when a
reasoning-capable model returns no visible content and is also unset by
default. Set either variable to a positive value when a provider requires an
explicit completion limit.

### Local LLMs (Ollama, vLLM & Local Servers)

Hệ thống hỗ trợ các mô hình mã nguồn mở cục bộ chạy qua Ollama, vLLM hoặc LM Studio (cổng mặc định `http://localhost:11434/v1` hoặc cấu hình qua `LOCAL_BASE_URL`):
- **Các model cấu hình sẵn**:
  - `local-qwen-2.5-coder-14b`: Qwen 2.5 Coder 14B (Ollama: `qwen2.5-coder:14b`)
  - `local-qwen-2.5-coder-7b`: Qwen 2.5 Coder 7B (Ollama: `qwen2.5-coder:7b`)
  - `local-qwen3-4b`: Qwen3 4B (Ollama: `qwen3:4b`)
  - `local-qwen-2.5-14b`, `local-qwen-2.5-7b`, `local-qwen-2.5-3b`
  - `local-deepseek-coder-6.7b`, `local-llama-3.1-8b`
- **Cú pháp Ad-hoc**:
  Chạy bất kỳ model local nào bằng tiền tố `local:`:
  ```bash
  cd automation
  python cli_experiment_runner.py --model "local:qwen2.5-coder:14b" --strategy simple_prompting --context full_context
  ```

### Kaggle Dual-GPU Testing & Benchmarking ($0 API Cost)

Dự án cung cấp bộ công cụ tối ưu hóa riêng cho môi trường **Kaggle Dual-GPU (2x Tesla T4 15GB)** hoàn toàn miễn phí.

> **Lưu ý**: Tùy chọn Kaggle được thiết kế chuyên biệt để chạy qua **dòng lệnh (CMD / Terminal)** hoặc **Jupyter Notebook** trên Kaggle, **không đẩy lên giao diện Web (Streamlit)** để bảo vệ VRAM server. Ưu tiên sử dụng **modelbase gốc** (`Qwen/Qwen2.5-Coder-7B-Instruct` hoặc `14B`) kết hợp **chuẩn NF4 (4-bit)** để chống tràn VRAM.

- **Kiến trúc Dual-GPU MoA (`CouncilEngine`)**:
  - **GPU 0 (cuda:0)**: Coder Model `Qwen/Qwen2.5-Coder-7B-Instruct` (hoặc `14B`) chuẩn NF4 4-bit (~4.5GB - 8.5GB VRAM).
  - **GPU 1 (cuda:1)**: Critic Model `Qwen/Qwen3-4B-Instruct-2507` chuẩn NF4 4-bit (~3.2GB VRAM).
- **Notebook tương tác**: [`kaggle/kaggle_test_generator.ipynb`](kaggle/kaggle_test_generator.ipynb) — Có thể import trực tiếp vào Kaggle Notebook, chọn Accelerator `GPU T4 x2` và chạy "Run All".
- **Council CLI Runner**: [`council_runner.py`](council_runner.py) / [`kaggle/kaggle_dual_gpu_runner.py`](kaggle/kaggle_dual_gpu_runner.py):
  ```bash
  # Chạy Council (Coder 7B + Critic 4B) với chuẩn NF4 4-bit:
  python council_runner.py --mode council --load-in-4bit

  # Chạy ma trận đầy đủ (2 chiến lược × 3 context):
  python council_runner.py --mode full_scenario --load-in-4bit

  # Chạy test nhanh không tải trọng số (Mock mode):
  python council_runner.py --mock --mode council
  ```
- Chi tiết xem tại [Hướng dẫn Kaggle](kaggle/README_KAGGLE.md).

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
- All 720 baseline experiments are stored in `automation/cli_results_v3/`
- Additional frontier & open-weight model runs are stored in:
  - `automation/cli_results_v1/`: Nemotron 3 Super 120B
  - `automation/cli_results_v10/`: Groq GPT-OSS 120B
  - `automation/cli_results_v11/`: Groq GPT-OSS 20B
- Aggregated synthesis datasets, charts, and report templates are in `automation/synthesis_output/`
- Academic paper and presentation files are in `automation/docs/`
- To regenerate the full synthesis reports and SVG charts:
  ```bash
  python3 automation/generate_synthesis_report.py
  ```
