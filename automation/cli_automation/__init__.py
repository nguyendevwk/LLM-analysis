"""
CLI-based LLM automation package

This package provides clients for various LLM backends:
- OpenAI-compatible API clients for free providers (APIClient):
  OpenRouter, Groq, Gemini API, local servers — API key only, no CLI tools
- Claude Code CLI (ClaudeCodeClient)
- Google Gemini CLI (GeminiCLIClient)

All clients inherit from BaseCLIClient for consistent interface.

Usage:
    from cli_automation import ClaudeCodeClient, GeminiCLIClient, APIClient

    # Claude Code
    with ClaudeCodeClient(model="claude-sonnet-4.5") as client:
        response = client.send_prompt("Write tests...")

    # Gemini CLI
    with GeminiCLIClient(model="gemini-2.5-flash") as client:
        response = client.send_prompt("Write tests...")

    # Free provider via API key (OpenRouter / Groq / Gemini API)
    with APIClient(provider="openrouter", model="google/gemma-4-31b-it:free") as client:
        response = client.send_prompt("Write tests...")
"""

from .base_cli_client import BaseCLIClient
from .claude_code_client import ClaudeCodeClient
from .gemini_cli_client import GeminiCLIClient
from .api_client import APIClient, PROVIDERS, load_dotenv
from .hf_client import HuggingFaceClient

__all__ = [
    'BaseCLIClient',
    'ClaudeCodeClient',
    'GeminiCLIClient',
    'APIClient',
    'HuggingFaceClient',
    'PROVIDERS',
    'load_dotenv',
]

__version__ = '1.2.0'
