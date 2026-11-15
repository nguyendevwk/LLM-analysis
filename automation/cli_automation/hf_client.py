"""
Hugging Face Transformers Client for Local GPU Inference.

Enables local test generation using open-source models (e.g., Qwen 2.5 Coder 14B,
Qwen3 4B, Llama 3.1) directly on local GPUs or Kaggle Dual-GPU (2x Tesla T4)
with 4-bit NF4 quantization ($0 API cost).
"""

import os
import sys
import time
import logging
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path

from .base_cli_client import BaseCLIClient

logger = logging.getLogger(__name__)

# Common friendly aliases mapped to Hugging Face model IDs
HF_MODEL_ALIASES: Dict[str, str] = {
    # Qwen 2.5 Coder
    "qwen2.5-coder:14b": "Qwen/Qwen2.5-Coder-14B-Instruct",
    "qwen2.5-coder-14b": "Qwen/Qwen2.5-Coder-14B-Instruct",
    "qwen-coder-14b": "Qwen/Qwen2.5-Coder-14B-Instruct",
    "qwen2.5-coder:7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "qwen2.5-coder-7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "qwen-coder-7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "qwen2.5-coder:1.5b": "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    "qwen2.5-coder:32b": "Qwen/Qwen2.5-Coder-32B-Instruct",

    # Qwen 3 & Qwen 2.5 General
    "qwen3:4b": "Qwen/Qwen3-4B-Instruct-2507",
    "qwen3-4b": "Qwen/Qwen3-4B-Instruct-2507",
    "qwen3-4b-instruct": "Qwen/Qwen3-4B-Instruct-2507",
    "qwen2.5:3b": "Qwen/Qwen2.5-3B-Instruct",
    "qwen2.5-3b": "Qwen/Qwen2.5-3B-Instruct",
    "qwen2.5:7b": "Qwen/Qwen2.5-7B-Instruct",
    "qwen2.5-7b": "Qwen/Qwen2.5-7B-Instruct",
    "qwen2.5:14b": "Qwen/Qwen2.5-14B-Instruct",
    "qwen2.5-14b": "Qwen/Qwen2.5-14B-Instruct",

    # Llama & DeepSeek
    "llama3.1:8b": "meta-llama/Llama-3.1-8B-Instruct",
    "deepseek-coder:6.7b": "deepseek-ai/deepseek-coder-6.7b-instruct",
}


class HuggingFaceClient(BaseCLIClient):
    """
    Client for local Hugging Face Transformers models.

    Supports 4-bit NF4 quantization via bitsandbytes to run large models
    (such as Qwen 2.5 Coder 14B) within 15 GB VRAM limits (e.g. Tesla T4).
    """

    def __init__(
        self,
        model: str,
        device: Optional[str] = None,
        load_in_4bit: bool = True,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        timeout: int = 600,
        **kwargs
    ):
        """
        Initialize the Hugging Face client.

        Args:
            model: Hugging Face repo ID or friendly alias (e.g. 'qwen2.5-coder:14b')
            device: Specific device ('cuda:0', 'cuda:1', 'cpu', or 'auto')
            load_in_4bit: Whether to load with 4-bit NF4 quantization
            temperature: Sampling temperature (default: 0.2)
            max_tokens: Max new tokens to generate (default: 2048)
            api_key: Optional Hugging Face token (or HF_TOKEN env var)
            timeout: Generation timeout in seconds
        """
        resolved_model = HF_MODEL_ALIASES.get(model.lower(), model)
        super().__init__(command="transformers", model=resolved_model, timeout=timeout)

        self.model_id = resolved_model
        self.device = device or ("cuda" if self._has_cuda() else "cpu")
        self.load_in_4bit = load_in_4bit and self._has_cuda()
        self.temperature = temperature if temperature is not None else float(os.environ.get("LLM_TEMPERATURE", "0.2"))
        self.max_tokens = max_tokens if max_tokens is not None else int(os.environ.get("LLM_MAX_TOKENS", "2048"))
        self.hf_token = api_key or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")

        self._model_obj = None
        self._tokenizer = None

    @staticmethod
    def _has_cuda() -> bool:
        """Check if CUDA is available without throwing if torch is not installed."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def _ensure_loaded(self):
        """Lazy-load model and tokenizer when needed."""
        if self._model_obj is not None and self._tokenizer is not None:
            return

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as e:
            raise RuntimeError(
                "HuggingFace direct inference requires 'torch' and 'transformers'.\n"
                "Install them via: pip install torch transformers accelerate bitsandbytes\n"
                "Or run via local OpenAI server (Ollama/vLLM) with provider 'local'."
            ) from e

        logger.info(f"Loading Hugging Face model '{self.model_id}' onto {self.device}...")
        start_t = time.time()

        tokenizer_kwargs = {"trust_remote_code": True}
        if self.hf_token:
            tokenizer_kwargs["token"] = self.hf_token

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_id, **tokenizer_kwargs)
        except Exception:
            # Fallback for preview models if repo is gated or renamed
            fallback = "Qwen/Qwen2.5-Coder-7B-Instruct"
            logger.warning(f"Could not load tokenizer for '{self.model_id}', falling back to '{fallback}'")
            self.model_id = fallback
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_id, **tokenizer_kwargs)

        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

        model_kwargs: Dict[str, Any] = {
            "trust_remote_code": True,
        }
        if self.hf_token:
            model_kwargs["token"] = self.hf_token

        if self.load_in_4bit and torch.cuda.is_available():
            try:
                from transformers import BitsAndBytesConfig
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["device_map"] = {"": self.device} if self.device != "auto" else "auto"
                logger.info("Using 4-bit NF4 quantization for memory efficiency (~8.5GB VRAM for 14B).")
            except Exception as quant_err:
                logger.warning(f"BitsAndBytes 4-bit quantization failed: {quant_err}. Falling back to float16.")
                model_kwargs["torch_dtype"] = torch.float16
                model_kwargs["device_map"] = "auto"
        else:
            if torch.cuda.is_available():
                model_kwargs["torch_dtype"] = torch.float16
                model_kwargs["device_map"] = {"": self.device} if self.device != "auto" else "auto"
            else:
                model_kwargs["torch_dtype"] = torch.float32

        self._model_obj = AutoModelForCausalLM.from_pretrained(self.model_id, **model_kwargs)
        logger.info(f"Model '{self.model_id}' successfully loaded in {time.time() - start_t:.2f}s.")

    def send_prompt(self, prompt: str) -> Optional[str]:
        """Send a single prompt and return generated text."""
        messages = [{"role": "user", "content": prompt}]
        return self._generate_messages(messages)

    def send_prompts_sequential(
        self,
        prompts: List[str]
    ) -> Tuple[List[str], str, float]:
        """Execute multiple prompts sequentially maintaining conversation history."""
        responses = []
        messages = []
        total_time = 0.0

        for prompt in prompts:
            messages.append({"role": "user", "content": prompt})
            resp = self._generate_messages(messages)
            if not resp:
                raise RuntimeError("Failed to generate response in sequential step")
            responses.append(resp)
            messages.append({"role": "assistant", "content": resp})
            total_time += self.last_response_time

        final_response = responses[-1] if responses else ""
        return responses, final_response, total_time

    def _generate_messages(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Perform text generation for chat messages."""
        self._ensure_loaded()
        import torch

        start_time = time.time()
        try:
            if hasattr(self._tokenizer, "apply_chat_template"):
                prompt_text = self._tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            else:
                prompt_text = "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages) + "\n\nASSISTANT:"

            inputs = self._tokenizer(prompt_text, return_tensors="pt")
            if torch.cuda.is_available() and self.device != "cpu":
                inputs = {k: v.to(self._model_obj.device) for k, v in inputs.items()}

            input_length = inputs["input_ids"].shape[1]

            gen_kwargs = {
                "max_new_tokens": self.max_tokens,
                "pad_token_id": self._tokenizer.pad_token_id,
                "eos_token_id": self._tokenizer.eos_token_id,
            }
            if self.temperature > 0.0:
                gen_kwargs["do_sample"] = True
                gen_kwargs["temperature"] = self.temperature
                gen_kwargs["top_p"] = 0.95
            else:
                gen_kwargs["do_sample"] = False

            with torch.no_grad():
                output_ids = self._model_obj.generate(**inputs, **gen_kwargs)

            generated_tokens = output_ids[0][input_length:]
            response_text = self._tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

            self.last_response_time = time.time() - start_time
            logger.info(
                f"Generated {len(generated_tokens)} tokens in {self.last_response_time:.2f}s "
                f"({len(generated_tokens) / max(self.last_response_time, 0.001):.1f} tok/s)"
            )
            return response_text

        except Exception as e:
            logger.error(f"Generation error with model '{self.model_id}': {e}", exc_info=True)
            self.last_response_time = time.time() - start_time
            return None

    def close(self):
        """Free GPU memory cache."""
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
