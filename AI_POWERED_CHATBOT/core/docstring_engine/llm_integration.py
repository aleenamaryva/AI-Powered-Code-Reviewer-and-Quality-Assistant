# core/docstring_engine/llm_integration.py
"""LLM integration layer for AI-powered docstring generation."""

from __future__ import annotations
import os
from typing import Optional


class LLMIntegration:
    """Wraps local or remote LLM backends for docstring generation.

    Supports:
      - Groq (cloud, fast inference)
      - Ollama (local, privacy-first)
      - OpenAI-compatible endpoints
    """

    SUPPORTED_BACKENDS = ("groq", "ollama", "openai")

    def __init__(self, backend: str = "groq", model: str | None = None):
        """Initialize the LLM integration.

        Args:
            backend (str): Backend to use — 'groq', 'ollama', or 'openai'.
            model (str | None): Model identifier. Uses backend default if None.

        Raises:
            ValueError: If an unsupported backend is specified.
        """
        if backend not in self.SUPPORTED_BACKENDS:
            raise ValueError(
                f"Unsupported backend '{backend}'. Choose from: {self.SUPPORTED_BACKENDS}"
            )
        self.backend = backend
        self.model = model or self._default_model(backend)
        self._client = None

    # ── Public API ─────────────────────────────────────────────────────────────

    def generate_docstring(
        self,
        func_name: str,
        source: str,
        style: str = "GOOGLE",
        extra_context: str = "",
    ) -> str:
        """Generate an AI docstring for a Python function using the configured LLM.

        Args:
            func_name (str): Name of the function to document.
            source (str): Full source code of the function.
            style (str): Docstring format — 'GOOGLE', 'NUMPY', or 'reST'.
            extra_context (str): Optional extra context injected into the prompt.

        Returns:
            str: Generated docstring text (without enclosing triple-quotes).
        """
        prompt = self._build_prompt(func_name, source, style, extra_context)
        return self._call_backend(prompt)

    def is_available(self) -> bool:
        """Check whether the configured backend is reachable.

        Returns:
            bool: True if the backend responded successfully to a ping.
        """
        try:
            self._call_backend("ping")
            return True
        except Exception:
            return False

    # ── Private helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _default_model(backend: str) -> str:
        """Return the default model identifier for a given backend.

        Args:
            backend (str): Backend name.

        Returns:
            str: Default model string.
        """
        defaults = {
            "groq": "llama3-8b-8192",
            "ollama": "mistral",
            "openai": "gpt-3.5-turbo",
        }
        return defaults.get(backend, "unknown")

    def _build_prompt(
        self, func_name: str, source: str, style: str, extra_context: str
    ) -> str:
        """Construct the prompt string for the LLM.

        Args:
            func_name (str): Function name.
            source (str): Function source code.
            style (str): Docstring style.
            extra_context (str): Additional context.

        Returns:
            str: Full prompt text.
        """
        context_block = f"\nExtra context: {extra_context}" if extra_context else ""
        return (
            f"You are a Python documentation expert.\n"
            f"Write a {style}-style docstring for the following function.\n"
            f"Return ONLY the docstring body — no surrounding triple-quotes.\n"
            f"{context_block}\n\n"
            f"Function: {func_name}\n"
            f"Source:\n```python\n{source}\n```"
        )

    def _call_backend(self, prompt: str) -> str:
        """Dispatch the prompt to the active backend.

        Args:
            prompt (str): Prompt string to send.

        Returns:
            str: Raw text response from the LLM.

        Raises:
            RuntimeError: If the backend call fails.
        """
        if self.backend == "groq":
            return self._call_groq(prompt)
        elif self.backend == "ollama":
            return self._call_ollama(prompt)
        elif self.backend == "openai":
            return self._call_openai(prompt)
        raise RuntimeError(f"Backend '{self.backend}' not implemented.")

    def _call_groq(self, prompt: str) -> str:
        """Call the Groq cloud API.

        Args:
            prompt (str): Prompt to send.

        Returns:
            str: Response text.

        Raises:
            RuntimeError: If the Groq SDK is missing or the API key is unset.
        """
        try:
            from groq import Groq  # type: ignore
        except ImportError as exc:
            raise RuntimeError("groq package not installed. Run: pip install groq") from exc

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY environment variable not set.")

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()

    def _call_ollama(self, prompt: str) -> str:
        """Call a local Ollama instance.

        Args:
            prompt (str): Prompt to send.

        Returns:
            str: Response text.

        Raises:
            RuntimeError: If the ollama package is missing or the request fails.
        """
        try:
            import ollama  # type: ignore
        except ImportError as exc:
            raise RuntimeError("ollama package not installed. Run: pip install ollama") from exc

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"].strip()

    def _call_openai(self, prompt: str) -> str:
        """Call an OpenAI-compatible API endpoint.

        Args:
            prompt (str): Prompt to send.

        Returns:
            str: Response text.

        Raises:
            RuntimeError: If the openai package is missing or the API key is unset.
        """
        try:
            import openai  # type: ignore
        except ImportError as exc:
            raise RuntimeError("openai package not installed. Run: pip install openai") from exc

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set.")

        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=512,
        )
        return response.choices[0].message["content"].strip()
