"""
OpenAI-Compatible API Client (free providers).

This module implements an HTTP client for any OpenAI-compatible
`/chat/completions` endpoint, so experiments can run with nothing but an
API key — no CLI tools required. It is the entry point for reproducing the
paper's experiments on free/open providers:

    Provider    Base URL                                          Key env var
    ----------  ------------------------------------------------  -----------------
    openrouter  https://openrouter.ai/api/v1                     OPENROUTER_API_KEY
    groq        https://api.groq.com/openai/v1                   GROQ_API_KEY
    gemini      https://generativelanguage.googleapis.com/...     GEMINI_API_KEY
                (v1beta/openai — Gemini's OpenAI-compatible API)
    local       http://localhost:11434/v1 (override via env)      LOCAL_API_KEY (optional)

Authentication:
    Put the key in a `.env` file at the repository root (see `.env.example`)
    or export it as an environment variable.

Configuration (env vars, all optional):
    LLM_TEMPERATURE   Sampling temperature (default: 0.2; 0 = greedy)
    LLM_MAX_TOKENS    Max completion tokens (unset, 0 or empty =
                      no client-side limit — omit the parameter and let the
                      provider decide)
    LLM_RECOVERY_MAX_TOKENS
                      Completion limit for one retry after an empty
                      reasoning-only response (unset by default)
    LLM_TIMEOUT       Request timeout in seconds (default: 300)
    LLM_MAX_RETRIES   Attempts per request incl. backoff (default: 4)
    <PROVIDER>_BASE_URL   Override the provider base URL (tests, proxies,
                          local servers such as Ollama/LM Studio/vLLM)
    <PROVIDER>_API_KEY_SLOT
                          Use exactly one numbered key (slot 1 is the base
                          variable; kept for backwards compatibility)
    <PROVIDER>_API_KEY_START_SLOT
                          Start with this key and keep later numbered keys as
                          quota fallbacks, e.g. GEMINI_API_KEY_START_SLOT=3

Technical Details:
    - Inherits BaseCLIClient, so Chain-of-Thought sequential prompting
      (send_prompts_sequential) works unchanged.
    - Retries with exponential backoff on 429/5xx/timeouts (free tiers are
      rate-limited) and honours `Retry-After` when present.
    - `command` is set to "api:<provider>" so prompt strategies detect a
      non-shell client and use the sequential-prompt path.
"""

import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

from .base_cli_client import BaseCLIClient

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]

PROVIDERS: Dict[str, Dict] = {
    "openrouter": {
        "label": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_API_KEY",
        "extra_headers": {
            "X-Title": "LLM Test Generation Analysis",
            "HTTP-Referer": "https://github.com/nguyendevwk/LLM-analysis",
        },
        "key_required": True,
    },
    "groq": {
        "label": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "extra_headers": {},
        "key_required": True,
    },
    "gemini": {
        "label": "Google Gemini API",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "key_env": "GEMINI_API_KEY",
        "extra_headers": {},
        "key_required": True,
    },
    "local": {
        "label": "Local OpenAI-compatible server",
        "base_url": "http://localhost:11434/v1",
        "key_env": "LOCAL_API_KEY",
        "extra_headers": {},
        "key_required": False,
    },
    "intern-ai": {
        "label": "InternAI / Discovery API",
        "base_url": "https://discovery-api.intern-ai.org.cn/v1",
        "key_env": "INTERNAI_API_KEY",
        "extra_headers": {},
        "key_required": True,
    },
}

_env_loaded = False


def _parse_max_tokens(raw: Optional[str]) -> Optional[int]:
    """
    Parse the LLM_MAX_TOKENS env var.

    Returns None (no limit — the parameter is omitted from the request) when
    the value is empty, "0" or "none"; otherwise the integer value.
    """
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in ("", "0", "none", "unlimited"):
        return None
    return int(value)


def load_dotenv() -> None:
    """
    Load KEY=VALUE pairs from the first `.env` file found.

    Search order: ./.env, ../.env, <repo root>/.env. Existing environment
    variables are never overridden. The file is read at most once per process.
    """
    global _env_loaded
    if _env_loaded:
        return

    candidates = [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        REPO_ROOT / ".env",
    ]

    for env_file in candidates:
        if not env_file.is_file():
            continue
        try:
            for raw_line in env_file.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key:
                    os.environ.setdefault(key, value)
            logger.info("Loaded environment variables from %s", env_file)
        except OSError as e:
            logger.warning("Could not read %s: %s", env_file, e)
        break

    _env_loaded = True


class APIClient(BaseCLIClient):
    """
    Client for OpenAI-compatible chat completion APIs (free providers).

    Attributes:
        SUPPORTED_PROVIDERS: Keys of PROVIDERS this client accepts
        provider: Provider key (openrouter/groq/gemini/local)
        model: Provider-native model identifier
        last_response_time: Duration of the last request in seconds
    """

    SUPPORTED_PROVIDERS = list(PROVIDERS.keys())

    def __init__(
        self,
        provider: str,
        model: str,
        timeout: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the API client.

        Args:
            provider: One of 'openrouter', 'groq', 'gemini', 'local'
            model: Provider-native model id (e.g. 'google/gemma-4-31b-it:free')
            timeout: Request timeout in seconds (default: LLM_TIMEOUT or 300)
            temperature: Sampling temperature (default: LLM_TEMPERATURE or 0.2)
            max_tokens: Optional completion-token limit. When unset, the
                        request omits ``max_tokens``.

        Raises:
            ValueError: If the provider is unknown
            RuntimeError: If requests is missing or the API key is not set
        """
        load_dotenv()

        if provider not in PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Supported providers: {', '.join(PROVIDERS)}"
            )

        config = PROVIDERS[provider]
        self.provider = provider
        self.provider_config = config
        self.base_url = os.environ.get(
            f"{provider.upper()}_BASE_URL", config["base_url"]
        ).rstrip("/")
        self.key_env = config["key_env"]
        if api_key and api_key.strip():
            self.api_keys = [api_key.strip()]
        else:
            self.api_keys = self._load_api_keys(self.key_env)
        self._api_key_index = 0
        self.api_key = self.api_keys[0] if self.api_keys else None
        self.key_required = config["key_required"]

        self.temperature = (
            temperature if temperature is not None
            else float(os.environ.get("LLM_TEMPERATURE", "0.2"))
        )
        self.max_tokens = (
            max_tokens if max_tokens is not None
            else _parse_max_tokens(os.environ.get("LLM_MAX_TOKENS"))
        )
        resolved_timeout = timeout or int(os.environ.get("LLM_TIMEOUT", "300"))
        self.max_retries = int(os.environ.get("LLM_MAX_RETRIES", "4"))

        # `command` marks the client type for prompt strategies (CLI-mode
        # sequential prompting) without spawning any subprocess.
        super().__init__(
            command=f"api:{provider}", model=model, timeout=resolved_timeout
        )

        if not self.check_installation():
            raise RuntimeError(
                f"{config['label']} is not ready: set {self.key_env} "
                f"in <repo>/.env or as an environment variable "
                f"(see .env.example), or install 'requests'."
            )

        logger.info(
            "API client initialized: provider=%s, model=%s, base_url=%s",
            provider, model, self.base_url
        )

    def check_installation(self) -> bool:
        """
        Verify that requests is available and the API key (if required) is set.

        Returns:
            True if the client can run, False otherwise
        """
        try:
            import requests  # noqa: F401
        except ImportError:
            logger.error("'requests' is not installed — run: uv sync")
            return False

        if self.key_required and not self.api_key:
            logger.error(
                "No %s found (checked environment and .env files)", self.key_env
            )
            return False

        return True

    def check_authentication(self) -> bool:
        """
        Verify the API key by querying the provider's /models endpoint.

        Returns:
            True if the endpoint is reachable and the key is accepted
        """
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self._headers(),
                timeout=20,
            )
            if response.status_code == 200:
                return True
            if response.status_code in (401, 403):
                logger.error(
                    "%s rejected the key (%s): %s",
                    self.provider_config["label"],
                    response.status_code,
                    response.text[:200],
                )
                return False
            logger.warning(
                "Unexpected status %s from %s/models — proceeding anyway",
                response.status_code, self.base_url
            )
            return True
        except requests.RequestException as e:
            logger.warning(
                "Could not verify %s authentication (%s) — proceeding anyway",
                self.provider_config["label"], e
            )
            return True

    def get_available_models(self) -> List[str]:
        """Return model ids listed by the provider's /models endpoint."""
        response = requests.get(
            f"{self.base_url}/models", headers=self._headers(), timeout=20
        )
        response.raise_for_status()
        data = response.json()
        return [m.get("id", "") for m in data.get("data", []) if m.get("id")]

    def send_prompt(self, prompt: str, **kwargs) -> str:
        """
        Send a single prompt to the chat completions API.

        Args:
            prompt: The prompt text to send
            **kwargs: Accepted for interface compatibility. ``is_final_step``
                controls code detection for sequential CoT requests.

        Returns:
            The model's response text

        Raises:
            RuntimeError: If the request fails after all retries
        """
        payload: Dict = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens

        response_text = self._post_chat_completions(payload)
        if kwargs.get("is_final_step", True):
            self._log_code_detection(response_text)
        else:
            logger.debug("Skipping code detection for an intermediate CoT step")
        return response_text

    def _headers(self) -> Dict[str, str]:
        """Build request headers for the provider."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        headers.update(self.provider_config.get("extra_headers", {}))
        return headers

    @staticmethod
    def _load_api_keys(base_key_env: str) -> List[str]:
        """Load one key or a consecutive, ordered set of quota fallbacks."""
        selected_slot = os.environ.get(f"{base_key_env}_SLOT")
        if selected_slot:
            try:
                slot = int(selected_slot)
            except ValueError as error:
                raise ValueError(
                    f"{base_key_env}_SLOT must be a positive integer"
                ) from error
            if slot < 1:
                raise ValueError(f"{base_key_env}_SLOT must be positive")
            key = os.environ.get(
                base_key_env if slot == 1 else f"{base_key_env}_{slot}"
            )
            return [key.strip()] if key else []

        start_slot_raw = os.environ.get(f"{base_key_env}_START_SLOT", "1")
        try:
            start_slot = int(start_slot_raw)
        except ValueError as error:
            raise ValueError(
                f"{base_key_env}_START_SLOT must be a positive integer"
            ) from error
        if start_slot < 1:
            raise ValueError(f"{base_key_env}_START_SLOT must be positive")

        key_names = [
            base_key_env if start_slot == 1 else f"{base_key_env}_{start_slot}"
        ]
        suffix = start_slot + 1
        while os.environ.get(f"{base_key_env}_{suffix}"):
            key_names.append(f"{base_key_env}_{suffix}")
            suffix += 1
        return [os.environ[name].strip() for name in key_names if os.environ.get(name)]

    @staticmethod
    def _is_quota_exhausted(response: requests.Response) -> bool:
        """Recognize quota exhaustion separately from transient rate limiting."""
        if response.status_code != 429:
            return False
        body = response.text.lower()
        return any(
            marker in body
            for marker in (
                "quota",
                "resource_exhausted",
                "daily limit",
                "per minute limit",
                "limit exceeded",
            )
        )

    def _rotate_api_key(self) -> bool:
        """Switch to the next configured key, returning whether one is available."""
        if len(self.api_keys) < 2:
            return False
        self._api_key_index = (self._api_key_index + 1) % len(self.api_keys)
        self.api_key = self.api_keys[self._api_key_index]
        logger.warning(
            "Rotating %s to configured fallback key %d/%d",
            self.key_env,
            self._api_key_index + 1,
            len(self.api_keys),
        )
        return True

    def _post_chat_completions(self, payload: Dict) -> str:
        """
        POST /chat/completions with retry/backoff logic.

        Retries on timeouts, connection errors, 429 and 5xx responses with
        exponential backoff (honouring `Retry-After`). A 400 caused by an
        unsupported `temperature` parameter is retried once without it.

        Raises:
            RuntimeError: On permanent failures (auth, missing model, ...)
            RuntimeError: If every attempt failed
        """
        url = f"{self.base_url}/chat/completions"
        drop_temperature = False
        recovery_max_tokens = (
            self.max_tokens
            or _parse_max_tokens(os.environ.get("LLM_RECOVERY_MAX_TOKENS"))
        )
        empty_completion_retried = False
        last_error = "no attempt made"

        for attempt in range(self.max_retries):
            body = dict(payload)
            if drop_temperature:
                body.pop("temperature", None)
            if empty_completion_retried:
                body["max_tokens"] = recovery_max_tokens

            start = time.time()
            try:
                response = requests.post(
                    url, headers=self._headers(), json=body, timeout=self.timeout
                )
                self.last_response_time = time.time() - start
            except requests.Timeout:
                self.last_response_time = time.time() - start
                last_error = f"timeout after {self.timeout}s"
                logger.warning(
                    "Attempt %d/%d timed out after %ds",
                    attempt + 1, self.max_retries, self.timeout
                )
            except requests.RequestException as e:
                self.last_response_time = time.time() - start
                last_error = str(e)
                logger.warning(
                    "Attempt %d/%d connection error: %s",
                    attempt + 1, self.max_retries, e
                )
            else:
                if response.status_code == 200:
                    try:
                        data = response.json()
                    except ValueError as e:
                        last_error = f"invalid JSON: {e}"
                        logger.warning("Invalid JSON response: %s", e)
                    else:
                        usage = data.get("usage")
                        if usage:
                            logger.info(
                                "Tokens — prompt: %s, completion: %s",
                                usage.get("prompt_tokens"),
                                usage.get("completion_tokens"),
                            )
                        try:
                            return self._extract_content(data)
                        except RuntimeError as error:
                            if not empty_completion_retried:
                                finish_reason = (data.get("choices") or [{}])[0].get(
                                    "finish_reason"
                                )
                                if recovery_max_tokens is None:
                                    logger.warning(
                                        "Model returned no visible content "
                                        "(finish_reason=%s); retrying without "
                                        "a max_tokens limit",
                                        finish_reason,
                                    )
                                else:
                                    logger.warning(
                                        "Model returned no visible content "
                                        "(finish_reason=%s); retrying with "
                                        "max_tokens=%d",
                                        finish_reason,
                                        recovery_max_tokens,
                                    )
                                empty_completion_retried = True
                                self._rotate_api_key()
                                if recovery_max_tokens is None:
                                    body.pop("max_tokens", None)
                                else:
                                    body["max_tokens"] = recovery_max_tokens
                                continue
                            raise error

                elif (
                    response.status_code == 400
                    and not drop_temperature
                    and "temperature" in payload
                    and "temperature" in response.text.lower()
                ):
                    logger.info(
                        "Provider rejected 'temperature' — retrying without it"
                    )
                    drop_temperature = True
                    continue

                elif (
                    response.status_code == 400
                    and "max_tokens" in body
                    and any(term in response.text.lower() for term in ("max_tokens", "max_completion_tokens"))
                ):
                    logger.info(
                        "Provider rejected 'max_tokens' — retrying with 'max_completion_tokens'"
                    )
                    payload["max_completion_tokens"] = payload.pop("max_tokens")
                    continue

                elif response.status_code == 402:
                    if self._rotate_api_key() and attempt < self.max_retries - 1:
                        continue
                    raise RuntimeError(
                        f"{self.provider_config['label']} returned 402 Payment Required "
                        f"(insufficient credits): {response.text[:300]}. "
                        "Please check your OpenRouter credit balance at https://openrouter.ai/credits "
                        f"or verify {self.key_env}."
                    )

                elif response.status_code in (401, 403):
                    if self._rotate_api_key() and attempt < self.max_retries - 1:
                        continue
                    raise RuntimeError(
                        f"{self.provider_config['label']} authentication failed "
                        f"({response.status_code}): {response.text[:300]}. "
                        f"Check {self.key_env}."
                    )

                elif response.status_code == 404:
                    if (
                        self._rotate_api_key()
                        and attempt < self.max_retries - 1
                        and any(
                            marker in response.text.lower()
                            for marker in ("zdr", "endpoint", "data policy")
                        )
                    ):
                        continue
                    restriction_hint = ""
                    if any(
                        marker in response.text.lower()
                        for marker in ("zdr", "data policy")
                    ):
                        restriction_hint = (
                            " This may be caused by OpenRouter account privacy/"
                            "ZDR settings; check the account associated with "
                            f"{self.key_env}."
                        )
                    raise RuntimeError(
                        f"Model '{self.model}' not found on "
                        f"{self.provider_config['label']} (404): "
                        f"{response.text[:300]}{restriction_hint}"
                    )

                elif response.status_code == 400:
                    raise RuntimeError(
                        f"{self.provider_config['label']} rejected the request "
                        f"(400): {response.text[:300]}"
                    )

                else:
                    last_error = (
                        f"HTTP {response.status_code}: {response.text[:300]}"
                    )
                    if response.status_code >= 500 or response.status_code == 429:
                        if self._is_quota_exhausted(response):
                            self._rotate_api_key()
                        retry_after = response.headers.get("Retry-After")
                        logger.warning(
                            "Attempt %d/%d got %s (Retry-After: %s)",
                            attempt + 1, self.max_retries,
                            response.status_code, retry_after
                        )
                        if retry_after and attempt < self.max_retries - 1:
                            try:
                                time.sleep(min(float(retry_after), 60.0))
                                continue
                            except ValueError:
                                pass
                    else:
                        raise RuntimeError(
                            f"{self.provider_config['label']} error {last_error}"
                        )

            if attempt < self.max_retries - 1:
                wait = 2 ** attempt
                logger.info("Waiting %ds before retry...", wait)
                time.sleep(wait)

        raise RuntimeError(
            f"All {self.max_retries} attempts failed for "
            f"{self.provider_config['label']} model '{self.model}': {last_error}"
        )

    def _extract_content(self, data: Dict) -> str:
        """
        Extract assistant text from an OpenAI-style chat completion payload.

        Handles string content, list-of-parts content, legacy `text` fields,
        and reports empty completions (e.g. reasoning-only models).
        """
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"No choices in response: {str(data)[:300]}")

        choice = choices[0]
        message = choice.get("message") or {}
        content = message.get("content")

        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, dict):
                    parts.append(part.get("text") or "")
                elif isinstance(part, str):
                    parts.append(part)
            content = "".join(parts)

        if not content:
            content = choice.get("text")

        if not content:
            reasoning = message.get("reasoning_content") or message.get("reasoning")
            hint = (
                " (model returned reasoning only — set LLM_MAX_TOKENS "
                "to a positive value or try a non-reasoning model)"
                if reasoning else ""
            )
            raise RuntimeError(f"Empty completion content from model{hint}")

        logger.info("Received response (%d chars)", len(content))
        return content

    @staticmethod
    def _is_recoverable_empty_completion(data: Dict) -> bool:
        """Identify reasoning-only or token-limit completions worth retrying."""
        choices = data.get("choices") or []
        if not choices:
            return False

        choice = choices[0] or {}
        message = choice.get("message") or {}
        has_reasoning = bool(
            message.get("reasoning_content") or message.get("reasoning")
        )
        finish_reason = choice.get("finish_reason")
        return has_reasoning or finish_reason in {"length", "max_tokens"}

    def _log_code_detection(self, text: str):
        """
        Log information about detected code in the response.

        Args:
            text: Response text to analyze
        """
        if '```python' in text:
            logger.debug("Response contains Python code blocks")
        elif '```' in text:
            logger.debug("Response contains generic code blocks")
        elif 'import unittest' in text or 'def test' in text:
            logger.debug("Response appears to be raw Python code")
        else:
            logger.warning("Response doesn't appear to contain code")

    def set_model(self, model: str):
        """Switch to a different model."""
        logger.info("Switched to model: %s", model)
        self.model = model

    def cleanup(self):
        """Release HTTP session resources."""
        logger.debug("Cleanup called for %s", self.__class__.__name__)
