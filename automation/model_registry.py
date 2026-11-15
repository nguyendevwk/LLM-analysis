"""
Model Registry for free/open providers.

Maps runner-facing model names to (provider, native model id) specs so the
paper's experiment matrix can be reproduced on free API providers with only
an API key — no CLI tools, no paid plan.

Two ways to address a model:

1. Registered name (filesystem-safe, also used as the results directory):
       openrouter-gemma-4-31b-it
       groq-gpt-oss-120b
       gemini-api-2.5-flash

2. Ad-hoc provider syntax for ANY model a provider offers:
       openrouter:google/gemma-4-31b-it:free
       groq:openai/gpt-oss-120b
       gemini:gemini-3.8-flash
       local:qwen2.5-coder:7b
   The canonical directory name is derived automatically ('/', ':' -> '-').

To add a curated model, append one line to REGISTRY below.

Note: OpenRouter free models end with ':free' — see
https://openrouter.ai/models?max_price=0 for the current list. Groq model ids:
https://console.groq.com/docs/models. Gemini model ids:
https://ai.google.dev/gemini-api/docs/models.
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

GROUP_GEMINI = "Gemini API"
GROUP_OPENROUTER_FREE = "OpenRouter (Free)"
GROUP_OPENROUTER_PAID = "OpenRouter (Paid)"
GROUP_OPENROUTER = GROUP_OPENROUTER_FREE  # Backwards compatibility
GROUP_GROQ = "Groq"
GROUP_LOCAL = "Local OpenAI-compatible server"
GROUP_HF = "HuggingFace Local GPU (Transformers/Kaggle)"
GROUP_INTERNAI = "InternAI / Discovery API"


@dataclass(frozen=True)
class ModelSpec:
    """Specification of one runnable model."""

    provider: str       # openrouter | groq | gemini | local
    model_id: str       # provider-native model identifier
    group: str          # display group for --list-models
    label: str          # human-readable name
    free: bool = True   # free-tier / open-weight model
    notes: str = ""


REGISTRY: Dict[str, ModelSpec] = {
    # --- Google Gemini API (AI Studio free tier, verified no billing) ---
    "gemini-api-3.8-flash": ModelSpec("gemini", "gemini-3.8-flash", GROUP_GEMINI, "Gemini 3.8 Flash"),
    "gemini-api-3.7-flash": ModelSpec("gemini", "gemini-3.7-flash", GROUP_GEMINI, "Gemini 3.7 Flash"),
    "gemini-api-3.6-flash": ModelSpec("gemini", "gemini-3.6-flash", GROUP_GEMINI, "Gemini 3.6 Flash"),
    "gemini-api-3.1-flash-lite": ModelSpec("gemini", "gemini-3.1-flash-lite", GROUP_GEMINI, "Gemini 3.1 Flash-Lite"),
    "gemini-api-3.5-flash": ModelSpec("gemini", "gemini-3.5-flash", GROUP_GEMINI, "Gemini 3.5 Flash"),
    "gemini-api-3.5-flash-lite": ModelSpec("gemini", "gemini-3.5-flash-lite", GROUP_GEMINI, "Gemini 3.5 Flash-Lite"),

    # --- Groq (free-plan models, verified against the account's model list) ---
    "groq-gpt-oss-120b": ModelSpec("groq", "openai/gpt-oss-120b", GROUP_GROQ, "GPT-OSS 120B"),
    "groq-gpt-oss-20b": ModelSpec("groq", "openai/gpt-oss-20b", GROUP_GROQ, "GPT-OSS 20B"),
    "groq-qwen3.8-27b": ModelSpec("groq", "qwen/qwen3.8-27b", GROUP_GROQ, "Qwen3.8 27B"),

    # --- OpenRouter (completely free ':free' models) ---
    "openrouter-gemma-4-31b-it": ModelSpec("openrouter", "google/gemma-4-31b-it:free", GROUP_OPENROUTER_FREE, "Gemma 4 31B IT"),
    "openrouter-gemma-4-26b-a4b-it": ModelSpec("openrouter", "google/gemma-4-26b-a4b-it:free", GROUP_OPENROUTER_FREE, "Gemma 4 26B A4B IT"),
    "openrouter-nemotron-3-super-120b-a12b": ModelSpec("openrouter", "nvidia/nemotron-3-super-120b-a12b:free", GROUP_OPENROUTER_FREE, "Nemotron 3 Super 120B"),
    "openrouter-nemotron-3.5-lightning": ModelSpec("openrouter", "nvidia/nemotron-3.5-lightning:free", GROUP_OPENROUTER_FREE, "Nemotron 3.5 Lightning"),
    "openrouter-nemotron-3-ultra-550b-a55b": ModelSpec("openrouter", "nvidia/nemotron-3-ultra-550b-a55b:free", GROUP_OPENROUTER_FREE, "Nemotron 3 Ultra 550B"),
    "openrouter-inkling": ModelSpec("openrouter", "thinkingmachines/inkling:free", GROUP_OPENROUTER_FREE, "Inkling"),
    "openrouter-inkling-small": ModelSpec("openrouter", "thinkingmachines/inkling-small:free", GROUP_OPENROUTER_FREE, "Inkling Small"),
    "openrouter-laguna-s-2.1": ModelSpec("openrouter", "poolside/laguna-s-2.1:free", GROUP_OPENROUTER_FREE, "Poolside Laguna S 2.1"),
    "openrouter-laguna-xs-2.1": ModelSpec("openrouter", "poolside/laguna-xs-2.1:free", GROUP_OPENROUTER_FREE, "Poolside Laguna XS 2.1"),
    "openrouter-north-mini-code": ModelSpec("openrouter", "cohere/north-mini-code:free", GROUP_OPENROUTER_FREE, "Cohere North Mini Code"),
    "openrouter-dots-3-note-preview": ModelSpec("openrouter", "dots-studio/dots-3-note-preview:free", GROUP_OPENROUTER_FREE, "DOTS.3 Note Preview"),
    "openrouter-lfm-2.5-2.6b": ModelSpec("openrouter", "liquid/lfm-2.5-2.6b:free", GROUP_OPENROUTER_FREE, "LFM 2.5 2.6B"),

    # --- OpenRouter (Commercial / Paid Models) ---
    # Anthropic
    "openrouter-claude-3.7-sonnet": ModelSpec("openrouter", "anthropic/claude-3.7-sonnet", GROUP_OPENROUTER_PAID, "Claude 3.7 Sonnet", free=False),
    "openrouter-claude-3.7-sonnet-thinking": ModelSpec("openrouter", "anthropic/claude-3.7-sonnet:thinking", GROUP_OPENROUTER_PAID, "Claude 3.7 Sonnet (Thinking)", free=False),
    "openrouter-claude-3.5-sonnet": ModelSpec("openrouter", "anthropic/claude-3.5-sonnet", GROUP_OPENROUTER_PAID, "Claude 3.5 Sonnet", free=False),
    "openrouter-claude-3.5-haiku": ModelSpec("openrouter", "anthropic/claude-3.5-haiku", GROUP_OPENROUTER_PAID, "Claude 3.5 Haiku", free=False),
    "openrouter-claude-3-opus": ModelSpec("openrouter", "anthropic/claude-3-opus", GROUP_OPENROUTER_PAID, "Claude 3 Opus", free=False),

    # OpenAI
    "openrouter-gpt-4o": ModelSpec("openrouter", "openai/gpt-4o", GROUP_OPENROUTER_PAID, "GPT-4o", free=False),
    "openrouter-gpt-4o-mini": ModelSpec("openrouter", "openai/gpt-4o-mini", GROUP_OPENROUTER_PAID, "GPT-4o mini", free=False),
    "openrouter-gpt-4.5-preview": ModelSpec("openrouter", "openai/gpt-4.5-preview", GROUP_OPENROUTER_PAID, "GPT-4.5 Preview", free=False),
    "openrouter-o3-mini": ModelSpec("openrouter", "openai/o3-mini", GROUP_OPENROUTER_PAID, "o3-mini", free=False),
    "openrouter-o1": ModelSpec("openrouter", "openai/o1", GROUP_OPENROUTER_PAID, "o1", free=False),
    "openrouter-o1-mini": ModelSpec("openrouter", "openai/o1-mini", GROUP_OPENROUTER_PAID, "o1-mini", free=False),

    # DeepSeek
    "openrouter-deepseek-v3": ModelSpec("openrouter", "deepseek/deepseek-chat", GROUP_OPENROUTER_PAID, "DeepSeek V3", free=False),
    "openrouter-deepseek-r1": ModelSpec("openrouter", "deepseek/deepseek-r1", GROUP_OPENROUTER_PAID, "DeepSeek R1", free=False),

    # Coding & Open-Weight Frontier
    "openrouter-qwen-2.5-coder-32b-instruct": ModelSpec("openrouter", "qwen/qwen-2.5-coder-32b-instruct", GROUP_OPENROUTER_PAID, "Qwen 2.5 Coder 32B", free=False),
    "openrouter-qwen-2.5-72b-instruct": ModelSpec("openrouter", "qwen/qwen-2.5-72b-instruct", GROUP_OPENROUTER_PAID, "Qwen 2.5 72B Instruct", free=False),
    "openrouter-codestral": ModelSpec("openrouter", "mistralai/codestral-2501", GROUP_OPENROUTER_PAID, "Codestral 2501", free=False),
    "openrouter-mistral-large": ModelSpec("openrouter", "mistralai/mistral-large-2411", GROUP_OPENROUTER_PAID, "Mistral Large 2411", free=False),
    "openrouter-llama-3.3-70b-instruct": ModelSpec("openrouter", "meta-llama/llama-3.3-70b-instruct", GROUP_OPENROUTER_PAID, "Llama 3.3 70B Instruct", free=False),
    "openrouter-llama-3.1-405b-instruct": ModelSpec("openrouter", "meta-llama/llama-3.1-405b-instruct", GROUP_OPENROUTER_PAID, "Llama 3.1 405B Instruct", free=False),

    # Google Gemini via OpenRouter
    "openrouter-gemini-2.0-flash": ModelSpec("openrouter", "google/gemini-2.0-flash-001", GROUP_OPENROUTER_PAID, "Gemini 2.0 Flash (OpenRouter)", free=False),
    "openrouter-gemini-2.5-pro": ModelSpec("openrouter", "google/gemini-2.5-pro", GROUP_OPENROUTER_PAID, "Gemini 2.5 Pro (OpenRouter)", free=False),

    # --- Local servers (Ollama / LM Studio / vLLM expose /v1) ---
    "local-qwen-2.5-coder-14b": ModelSpec("local", "qwen2.5-coder:14b", GROUP_LOCAL, "Qwen 2.5 Coder 14B (Local/Ollama)", notes="Ollama: qwen2.5-coder:14b | vLLM: Qwen/Qwen2.5-Coder-14B-Instruct"),
    "local-qwen-2.5-coder-7b": ModelSpec("local", "qwen2.5-coder:7b", GROUP_LOCAL, "Qwen 2.5 Coder 7B (Local/Ollama)", notes="Ollama: qwen2.5-coder:7b | vLLM: Qwen/Qwen2.5-Coder-7B-Instruct"),
    "local-qwen3-4b": ModelSpec("local", "qwen3:4b", GROUP_LOCAL, "Qwen3 4B (Local)", notes="Ollama: qwen3:4b | HF: Qwen/Qwen3-4B-Instruct-2507"),
    "local-qwen-2.5-14b": ModelSpec("local", "qwen2.5:14b", GROUP_LOCAL, "Qwen 2.5 14B (Local)", notes="Ollama: qwen2.5:14b"),
    "local-qwen-2.5-7b": ModelSpec("local", "qwen2.5:7b", GROUP_LOCAL, "Qwen 2.5 7B (Local)", notes="Ollama: qwen2.5:7b"),
    "local-qwen-2.5-3b": ModelSpec("local", "qwen2.5:3b", GROUP_LOCAL, "Qwen 2.5 3B (Local)", notes="Ollama: qwen2.5:3b"),
    "local-deepseek-coder-6.7b": ModelSpec("local", "deepseek-coder:6.7b", GROUP_LOCAL, "DeepSeek Coder 6.7B (Local)", notes="Ollama: deepseek-coder:6.7b"),
    "local-llama-3.1-8b": ModelSpec("local", "llama3.1:8b", GROUP_LOCAL, "Llama 3.1 8B (local)", notes="override LOCAL_BASE_URL if needed"),

    # --- Hugging Face Local GPU (Direct in-process inference / Kaggle Dual-GPU) ---
    "hf-qwen-2.5-coder-14b": ModelSpec("hf", "Qwen/Qwen2.5-Coder-14B-Instruct", GROUP_HF, "Qwen 2.5 Coder 14B (HF/Kaggle)", notes="4-bit NF4: ~8.5GB VRAM on Tesla T4"),
    "hf-qwen-2.5-coder-7b": ModelSpec("hf", "Qwen/Qwen2.5-Coder-7B-Instruct", GROUP_HF, "Qwen 2.5 Coder 7B (HF/Kaggle)", notes="4-bit NF4: ~4.5GB VRAM"),
    "hf-qwen3-4b": ModelSpec("hf", "Qwen/Qwen3-4B-Instruct-2507", GROUP_HF, "Qwen3 4B (HF/Kaggle)", notes="4-bit NF4: ~3.2GB VRAM on Tesla T4"),
    "hf-qwen-2.5-3b": ModelSpec("hf", "Qwen/Qwen2.5-3B-Instruct", GROUP_HF, "Qwen 2.5 3B (HF/Kaggle)", notes="4-bit NF4: ~2.8GB VRAM"),
    "hf-qwen-2.5-7b": ModelSpec("hf", "Qwen/Qwen2.5-7B-Instruct", GROUP_HF, "Qwen 2.5 7B (HF/Kaggle)", notes="4-bit NF4: ~4.5GB VRAM"),

    # --- InternAI / Discovery API (OpenAI-compatible) ---
    "intern-ai-glm-5-3": ModelSpec("intern-ai", "glm-5.3", GROUP_INTERNAI, "GLM 5.3"),
    "intern-ai-qwen3-8-27b": ModelSpec("intern-ai", "qwen3.8-27b", GROUP_INTERNAI, "Qwen3.8 27B"),
    "intern-ai-deepseek-v4-flash-0731": ModelSpec("intern-ai", "deepseek-v4-flash-0731", GROUP_INTERNAI, "DeepSeek V4 Flash 0731"),
}

# ---------------------------------------------------------------------------
# Temporarily disabled models (verified 2026-10-09 — paid or unavailable).
# Re-enable by moving an entry back into REGISTRY once access is confirmed:
#
#   Gemini (404 "no longer available to new users"):
#     "gemini-api-2.5-pro"        -> gemini-2.5-pro
#     "gemini-api-2.5-flash"      -> gemini-2.5-flash
#     "gemini-api-2.5-flash-lite" -> gemini-2.5-flash-lite
#   Gemini (429 quota — requires billing/credit card):
#     "gemini-api-3.1-pro"        -> gemini-3.1-pro-preview
#   Groq (404 "does not exist or you do not have access" — Enterprise models):
#     "groq-llama-3.3-70b"        -> llama-3.3-70b-versatile
#     "groq-llama-3.1-8b"         -> llama-3.1-8b-instant
#     "groq-minimax-m2.7"         -> minimaxai/minimax-m2.7
# ---------------------------------------------------------------------------


# Providers usable with ad-hoc "provider:model-id" syntax
PROVIDER_SYNTAX: Tuple[str, ...] = ("openrouter", "groq", "gemini", "local", "intern-ai", "hf")

PROVIDER_GROUPS = {
    "openrouter": GROUP_OPENROUTER_PAID,
    "groq": GROUP_GROQ,
    "gemini": GROUP_GEMINI,
    "local": GROUP_LOCAL,
    "hf": GROUP_HF,
    "intern-ai": GROUP_INTERNAI,
}


def canonical_name(provider: str, model_id: str) -> str:
    """
    Build a filesystem-safe runner/directory name for a provider model id.

    '/' and ':' are replaced with '-' so names like
    'openrouter:google/gemma-4-31b-it:free' become valid directory names.
    """
    safe = model_id.replace("/", "-").replace(":", "-").replace(" ", "_")
    return f"{provider}-{safe}"


def resolve_model(name: str) -> Optional[Tuple[ModelSpec, str]]:
    """
    Resolve a model name to (spec, canonical directory name).

    Accepts registered names ('groq-gpt-oss-120b', 'openrouter-claude-3.7-sonnet'),
    ad-hoc provider syntax ('openrouter:anthropic/claude-3.7-sonnet',
    'openrouter/openai/gpt-4o'), and direct vendor/model paths
    ('anthropic/claude-3.7-sonnet', 'openai/gpt-4o').
    Returns None when the name is neither — callers then fall back to legacy CLI
    models and raise a helpful error.
    """
    if name in REGISTRY:
        return REGISTRY[name], name

    for provider in PROVIDER_SYNTAX:
        for sep in (":", "/"):
            prefix = f"{provider}{sep}"
            if name.startswith(prefix):
                model_id = name[len(prefix):].strip()
                if not model_id:
                    return None
                is_free = ":free" in model_id.lower() or provider == "local"
                if provider == "openrouter":
                    group = GROUP_OPENROUTER_FREE if is_free else GROUP_OPENROUTER_PAID
                else:
                    group = PROVIDER_GROUPS.get(provider, provider)
                spec = ModelSpec(
                    provider=provider,
                    model_id=model_id,
                    group=group,
                    label=model_id,
                    free=is_free,
                    notes="ad-hoc (not in registry)",
                )
                return spec, canonical_name(provider, model_id)

    # If the user passed a vendor/model identifier directly, default to OpenRouter
    if "/" in name and not name.startswith(("./", "../", "/")):
        model_id = name.strip()
        is_free = ":free" in model_id.lower()
        spec = ModelSpec(
            provider="openrouter",
            model_id=model_id,
            group=GROUP_OPENROUTER_FREE if is_free else GROUP_OPENROUTER_PAID,
            label=model_id,
            free=is_free,
            notes="ad-hoc OpenRouter model",
        )
        return spec, canonical_name("openrouter", model_id)

    return None


def build_client_factories(**kwargs) -> Dict[str, Callable]:
    """
    Build {registered name: client factory} for all registry models.

    Factories are lazy: the API client or HuggingFace client is only created
    when an experiment actually runs. Any kwargs (e.g. temperature, max_tokens,
    api_key) are forwarded to the appropriate client.
    """
    factories: Dict[str, Callable] = {}
    for name, spec in REGISTRY.items():
        if spec.provider == "hf":
            factories[name] = (
                lambda model=spec.model_id, kw=kwargs:
                    _create_hf_client(model, **kw)
            )
        else:
            factories[name] = (
                lambda provider=spec.provider, model=spec.model_id, kw=kwargs:
                    _create_api_client(provider, model, **kw)
            )
    return factories


def _create_api_client(provider: str, model: str, **kwargs):
    from cli_automation import APIClient
    return APIClient(provider=provider, model=model, **kwargs)


def _create_hf_client(model: str, **kwargs):
    from cli_automation import HuggingFaceClient
    return HuggingFaceClient(model=model, **kwargs)


def make_client_factory(spec: ModelSpec, **kwargs) -> Callable:
    """Build a factory for an arbitrary (e.g. ad-hoc) model spec."""
    if spec.provider == "hf":
        return lambda: _create_hf_client(spec.model_id, **kwargs)
    return lambda: _create_api_client(spec.provider, spec.model_id, **kwargs)


def list_model_names() -> List[str]:
    """Return all registered model names."""
    return list(REGISTRY.keys())


def grouped_models() -> Dict[str, Dict[str, str]]:
    """Return {group: {model name: label}} for display purposes."""
    groups: Dict[str, Dict[str, str]] = {}
    for name, spec in REGISTRY.items():
        groups.setdefault(spec.group, {})[name] = spec.label
    return groups

