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

GROUP_GEMINI = "Gemini API (free tier — GEMINI_API_KEY)"
GROUP_OPENROUTER = "OpenRouter (free ':free' models — OPENROUTER_API_KEY)"
GROUP_GROQ = "Groq (free developer tier — GROQ_API_KEY)"
GROUP_LOCAL = "Local OpenAI-compatible server (LOCAL_API_KEY optional)"


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
    "gemini-api-3.5-flash": ModelSpec("gemini", "gemini-3.5-flash", GROUP_GEMINI, "Gemini 3.5 Flash"),
    "gemini-api-3.5-flash-lite": ModelSpec("gemini", "gemini-3.5-flash-lite", GROUP_GEMINI, "Gemini 3.5 Flash-Lite"),

    # --- Groq (free-plan models, verified against the account's model list) ---
    "groq-gpt-oss-120b": ModelSpec("groq", "openai/gpt-oss-120b", GROUP_GROQ, "GPT-OSS 120B"),
    "groq-gpt-oss-20b": ModelSpec("groq", "openai/gpt-oss-20b", GROUP_GROQ, "GPT-OSS 20B"),
    "groq-qwen3.8-27b": ModelSpec("groq", "qwen/qwen3.8-27b", GROUP_GROQ, "Qwen3.8 27B"),

    # --- OpenRouter (completely free ':free' models) ---
    "openrouter-gemma-4-31b-it": ModelSpec("openrouter", "google/gemma-4-31b-it:free", GROUP_OPENROUTER, "Gemma 4 31B IT"),
    "openrouter-gemma-4-26b-a4b-it": ModelSpec("openrouter", "google/gemma-4-26b-a4b-it:free", GROUP_OPENROUTER, "Gemma 4 26B A4B IT"),
    "openrouter-nemotron-3-super-120b-a12b": ModelSpec("openrouter", "nvidia/nemotron-3-super-120b-a12b:free", GROUP_OPENROUTER, "Nemotron 3 Super 120B"),
    "openrouter-nemotron-3.5-lightning": ModelSpec("openrouter", "nvidia/nemotron-3.5-lightning:free", GROUP_OPENROUTER, "Nemotron 3.5 Lightning"),
    "openrouter-nemotron-3-ultra-550b-a55b": ModelSpec("openrouter", "nvidia/nemotron-3-ultra-550b-a55b:free", GROUP_OPENROUTER, "Nemotron 3 Ultra 550B"),
    "openrouter-inkling": ModelSpec("openrouter", "thinkingmachines/inkling:free", GROUP_OPENROUTER, "Inkling"),
    "openrouter-inkling-small": ModelSpec("openrouter", "thinkingmachines/inkling-small:free", GROUP_OPENROUTER, "Inkling Small"),
    "openrouter-laguna-s-2.1": ModelSpec("openrouter", "poolside/laguna-s-2.1:free", GROUP_OPENROUTER, "Poolside Laguna S 2.1"),
    "openrouter-laguna-xs-2.1": ModelSpec("openrouter", "poolside/laguna-xs-2.1:free", GROUP_OPENROUTER, "Poolside Laguna XS 2.1"),
    "openrouter-north-mini-code": ModelSpec("openrouter", "cohere/north-mini-code:free", GROUP_OPENROUTER, "Cohere North Mini Code"),
    "openrouter-dots-3-note-preview": ModelSpec("openrouter", "dots-studio/dots-3-note-preview:free", GROUP_OPENROUTER, "DOTS.3 Note Preview"),
    "openrouter-lfm-2.5-2.6b": ModelSpec("openrouter", "liquid/lfm-2.5-2.6b:free", GROUP_OPENROUTER, "LFM 2.5 2.6B"),

    # --- Local servers (Ollama / LM Studio / vLLM expose /v1) ---
    "local-llama-3.1-8b": ModelSpec("local", "llama3.1:8b", GROUP_LOCAL, "Llama 3.1 8B (local)", notes="override LOCAL_BASE_URL if needed"),
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
PROVIDER_SYNTAX: Tuple[str, ...] = ("openrouter", "groq", "gemini", "local")

PROVIDER_GROUPS = {
    "openrouter": GROUP_OPENROUTER,
    "groq": GROUP_GROQ,
    "gemini": GROUP_GEMINI,
    "local": GROUP_LOCAL,
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

    Accepts registered names ('groq-gpt-oss-120b') and ad-hoc provider
    syntax ('openrouter:org/model:free'). Returns None when the name is
    neither — callers then fall back to legacy CLI models and raise a
    helpful error.
    """
    if name in REGISTRY:
        return REGISTRY[name], name

    for provider in PROVIDER_SYNTAX:
        prefix = f"{provider}:"
        if name.startswith(prefix):
            model_id = name[len(prefix):].strip()
            if not model_id:
                return None
            spec = ModelSpec(
                provider=provider,
                model_id=model_id,
                group=PROVIDER_GROUPS[provider],
                label=model_id,
                free=provider != "local",
                notes="ad-hoc (not in registry)",
            )
            return spec, canonical_name(provider, model_id)

    return None


def build_client_factories() -> Dict[str, Callable]:
    """
    Build {registered name: client factory} for all registry models.

    Factories are lazy: the API client (and its key check) is only created
    when an experiment actually runs.
    """
    from cli_automation import APIClient

    factories: Dict[str, Callable] = {}
    for name, spec in REGISTRY.items():
        factories[name] = (
            lambda provider=spec.provider, model=spec.model_id:
                APIClient(provider=provider, model=model)
        )
    return factories


def make_client_factory(spec: ModelSpec) -> Callable:
    """Build a factory for an arbitrary (e.g. ad-hoc) model spec."""
    from cli_automation import APIClient

    return lambda: APIClient(provider=spec.provider, model=spec.model_id)


def list_model_names() -> List[str]:
    """Return all registered model names."""
    return list(REGISTRY.keys())


def grouped_models() -> Dict[str, Dict[str, str]]:
    """Return {group: {model name: label}} for display purposes."""
    groups: Dict[str, Dict[str, str]] = {}
    for name, spec in REGISTRY.items():
        groups.setdefault(spec.group, {})[name] = spec.label
    return groups

