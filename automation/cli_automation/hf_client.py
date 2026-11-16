"""
Hugging Face Transformers Client for Local GPU Inference.

Enables local test generation using official open-source base models
(e.g., Qwen/Qwen2.5-Coder-14B-Instruct, Qwen/Qwen3-4B-Instruct-2507)
directly on local GPUs or Kaggle Dual-GPU (2x Tesla T4 15GB) with
standard on-the-fly 4-bit NF4 (NormalFloat4) quantization ($0 API cost).
"""

import os
import sys
import time
import logging
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path

# Optimize CUDA allocator to prevent virtual memory fragmentation
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

from .base_cli_client import BaseCLIClient

logger = logging.getLogger(__name__)

# Official base models mapped to friendly aliases (Base models only, standard NF4)
HF_MODEL_ALIASES: Dict[str, str] = {
    # Qwen 2.5 Coder Official Base Models
    "qwen2.5-coder:14b": "Qwen/Qwen2.5-Coder-14B-Instruct",
    "qwen2.5-coder-14b": "Qwen/Qwen2.5-Coder-14B-Instruct",
    "qwen2.5-coder-14": "Qwen/Qwen2.5-Coder-14B-Instruct",
    "qwen-coder-14b": "Qwen/Qwen2.5-Coder-14B-Instruct",
    "qwen2.5-coder:7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "qwen2.5-coder-7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "qwen2.5-coder-7": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "qwen-coder-7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "qwen2.5-coder:1.5b": "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    "qwen2.5-coder:32b": "Qwen/Qwen2.5-Coder-32B-Instruct",

    # Qwen 3 & Qwen 2.5 General Official Base Models
    "qwen3:4b": "Qwen/Qwen3-4B-Instruct-2507",
    "qwen3-4b": "Qwen/Qwen3-4B-Instruct-2507",
    "qwen3-4b-instruct": "Qwen/Qwen3-4B-Instruct-2507",
    "qwen2.5:3b": "Qwen/Qwen2.5-3B-Instruct",
    "qwen2.5-3b": "Qwen/Qwen2.5-3B-Instruct",
    "qwen2.5:7b": "Qwen/Qwen2.5-7B-Instruct",
    "qwen2.5-7b": "Qwen/Qwen2.5-7B-Instruct",
    "qwen2.5:14b": "Qwen/Qwen2.5-14B-Instruct",
    "qwen2.5-14b": "Qwen/Qwen2.5-14B-Instruct",

    # Llama & DeepSeek Official Base Models
    "llama3.1:8b": "meta-llama/Llama-3.1-8B-Instruct",
    "deepseek-coder:6.7b": "deepseek-ai/deepseek-coder-6.7b-instruct",
}


def ensure_bitsandbytes() -> bool:
    """Ensure bitsandbytes>=0.46.1 is installed for standard NF4 quantization."""
    try:
        import bitsandbytes  # noqa: F401
        return True
    except ImportError:
        logger.info("bitsandbytes not found. Auto-installing 'bitsandbytes>=0.46.1'...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-U", "bitsandbytes>=0.46.1"])
            import bitsandbytes  # noqa: F401
            logger.info("Successfully installed bitsandbytes.")
            return True
        except Exception as e:
            logger.warning(f"Could not auto-install bitsandbytes: {e}")
            return False


class HuggingFaceClient(BaseCLIClient):
    """
    Client for local Hugging Face Transformers base models.

    Applies standard on-the-fly 4-bit NF4 quantization via bitsandbytes
    to run large official base models (e.g. Qwen/Qwen2.5-Coder-14B-Instruct)
    within 15 GB VRAM limits (Tesla T4) without exceeding memory.
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
            model: Official Hugging Face model ID or alias (e.g. 'Qwen/Qwen2.5-Coder-14B-Instruct')
            device: Specific device ('cuda:0', 'cuda:1', 'cpu', or 'auto')
            load_in_4bit: Whether to apply standard 4-bit NF4 quantization
            temperature: Sampling temperature (default: 0.2)
            max_tokens: Max new tokens to generate (default: 2048)
            api_key: Optional Hugging Face token (or HF_TOKEN env var)
            timeout: Generation timeout in seconds
        """
        resolved_model = HF_MODEL_ALIASES.get(model.lower(), model)
        super().__init__(command="transformers", model=resolved_model, timeout=timeout)

        self.model_id = resolved_model
        if device:
            self.device = device
        else:
            if self._has_cuda():
                try:
                    import torch
                    self.device = "auto" if torch.cuda.device_count() > 1 else "cuda"
                except Exception:
                    self.device = "cuda"
            else:
                self.device = "cpu"

        self.load_in_4bit = load_in_4bit and self._has_cuda()
        self.temperature = temperature if temperature is not None else float(os.environ.get("LLM_TEMPERATURE", "0.2"))
        self.max_tokens = max_tokens if max_tokens is not None else int(os.environ.get("LLM_MAX_TOKENS", "2048"))
        self.hf_token = api_key or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")

        self._model_obj = None
        self._tokenizer = None

    def check_installation(self) -> bool:
        """Verify that PyTorch and Transformers are installed."""
        try:
            import torch  # noqa: F401
            import transformers  # noqa: F401
            return True
        except ImportError:
            logger.error(
                "PyTorch and Hugging Face Transformers are required.\n"
                "Install them via: pip install torch transformers accelerate 'bitsandbytes>=0.46.1'"
            )
            return False

    def check_authentication(self) -> bool:
        """Verify authentication (Qwen models are open-weights, no token strictly required)."""
        return True

    @staticmethod
    def _has_cuda() -> bool:
        """Check if CUDA is available without throwing if torch is not installed."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def _ensure_loaded(self):
        """Lazy-load base model and tokenizer with standard NF4 quantization."""
        if self._model_obj is not None and self._tokenizer is not None:
            return

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as e:
            raise RuntimeError(
                "HuggingFace direct inference requires 'torch' and 'transformers'.\n"
                "Install them via: pip install torch transformers accelerate 'bitsandbytes>=0.46.1'\n"
                "Or run via local OpenAI server (Ollama/vLLM) with provider 'local'."
            ) from e

        logger.info(f"Loading official base model '{self.model_id}' onto {self.device} (Standard NF4 4-bit)...")
        start_t = time.time()

        tokenizer_kwargs = {"trust_remote_code": True}
        if self.hf_token:
            tokenizer_kwargs["token"] = self.hf_token

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_id, **tokenizer_kwargs)
        except Exception:
            fallback = "Qwen/Qwen2.5-Coder-7B-Instruct"
            logger.warning(f"Could not load tokenizer for '{self.model_id}', falling back to '{fallback}'")
            self.model_id = fallback
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_id, **tokenizer_kwargs)

        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

        model_kwargs: Dict[str, Any] = {
            "trust_remote_code": True,
            "low_cpu_mem_usage": True,
        }
        if self.hf_token:
            model_kwargs["token"] = self.hf_token

        cuda_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
        is_large_model = any(tag in self.model_id.lower() for tag in ["14b", "32b", "70b"])

        # Multi-GPU auto-split (e.g. Kaggle Dual-GPU 2x Tesla T4) or RAM offloading for large 14B+ models
        if self.device == "auto" or cuda_count > 1 or is_large_model:
            model_kwargs["device_map"] = "auto"
            if cuda_count > 0:
                max_mem = {i: "13GiB" for i in range(cuda_count)}
                max_mem["cpu"] = "28GiB"
                model_kwargs["max_memory"] = max_mem
        else:
            model_kwargs["device_map"] = {"": self.device}

        if self.load_in_4bit and torch.cuda.is_available():
            ensure_bitsandbytes()
            try:
                from transformers import BitsAndBytesConfig
                compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=compute_dtype,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
                model_kwargs["quantization_config"] = quantization_config
                logger.info(f"Loaded with standard NF4 quantization (compute_dtype={compute_dtype}, device_map={model_kwargs['device_map']}).")
            except Exception as quant_err:
                logger.warning(f"BitsAndBytes NF4 quantization failed: {quant_err}. Falling back to float16.")
                model_kwargs["torch_dtype"] = torch.float16
        else:
            if torch.cuda.is_available():
                model_kwargs["torch_dtype"] = torch.float16
            else:
                model_kwargs["torch_dtype"] = torch.float32

        self._model_obj = AutoModelForCausalLM.from_pretrained(self.model_id, **model_kwargs)
        logger.info(f"Model '{self.model_id}' successfully loaded in {time.time() - start_t:.2f}s.")

    def send_prompt(self, prompt: str, **kwargs) -> Optional[str]:
        """Send a single prompt and return generated text."""
        messages = [{"role": "user", "content": prompt}]
        return self._generate_messages(messages)

    def send_prompts_sequential(
        self,
        prompts: List[str]
    ) -> Tuple[List[str], str, float]:
        """Execute multiple prompts sequentially maintaining conversation history."""
        import gc
        import torch

        responses = []
        messages = []
        total_time = 0.0

        for prompt in prompts:
            # Purge memory cache before each turn
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            messages.append({"role": "user", "content": prompt})
            resp = self._generate_messages(messages)
            if not resp:
                raise RuntimeError("Failed to generate response in sequential step")
            responses.append(resp)
            messages.append({"role": "assistant", "content": resp})
            total_time += self.last_response_time

            # Purge intermediate generation cache immediately after turn
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        final_response = responses[-1] if responses else ""
        return responses, final_response, total_time

    def _generate_messages(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Perform text generation for chat messages."""
        self._ensure_loaded()
        import torch
        import gc

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
                try:
                    target_device = next(self._model_obj.parameters()).device
                except Exception:
                    target_device = "cuda:0"
                inputs = {k: v.to(target_device) for k, v in inputs.items()}

            input_length = inputs["input_ids"].shape[1]

            gen_kwargs = {
                "max_new_tokens": self.max_tokens,
                "pad_token_id": self._tokenizer.pad_token_id,
                "eos_token_id": self._tokenizer.eos_token_id,
                "use_cache": True,
            }
            if self.temperature > 0.0:
                gen_kwargs["do_sample"] = True
                gen_kwargs["temperature"] = self.temperature
                gen_kwargs["top_p"] = 0.95
            else:
                gen_kwargs["do_sample"] = False

            with torch.inference_mode():
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
            err_msg = str(e).lower()
            if "out of memory" in err_msg or "cuda" in err_msg:
                logger.error(f"CUDA memory pressure with model '{self.model_id}': {e}. Purging memory cache...")
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            logger.error(f"Generation error with model '{self.model_id}': {e}", exc_info=True)
            self.last_response_time = time.time() - start_time
            return None
        finally:
            try:
                del inputs
            except Exception:
                pass
            try:
                del output_ids
            except Exception:
                pass
            try:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass

    def unload_model(self):
        """Completely unload model, delete tensors, garbage collect and free VRAM."""
        try:
            import gc
            import torch

            if self._model_obj is not None:
                try:
                    self._model_obj.to("cpu")
                except Exception:
                    pass
                del self._model_obj
                self._model_obj = None

            if self._tokenizer is not None:
                del self._tokenizer
                self._tokenizer = None

            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                if hasattr(torch.cuda, "ipc_collect"):
                    torch.cuda.ipc_collect()
                alloc_gb = torch.cuda.memory_allocated() / (1024 ** 3)
                res_gb = torch.cuda.memory_reserved() / (1024 ** 3)
                logger.info(
                    f"Model '{self.model_id}' unloaded. VRAM freed: {alloc_gb:.2f}GB allocated, {res_gb:.2f}GB reserved."
                )
        except Exception as e:
            logger.warning(f"Error while releasing VRAM: {e}")

    def close(self):
        """Free GPU memory cache and unload model."""
        self.unload_model()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
