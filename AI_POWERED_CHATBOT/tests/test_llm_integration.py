# tests/test_llm_integration.py
"""Unit tests for core.docstring_engine.llm_integration.LLMIntegration."""

import pytest
from unittest.mock import patch, MagicMock
from core.docstring_engine.llm_integration import LLMIntegration


# ── Instantiation ──────────────────────────────────────────────────────────────

class TestInit:
    def test_default_backend(self):
        llm = LLMIntegration()
        assert llm.backend == "groq"

    def test_custom_backend(self):
        llm = LLMIntegration(backend="ollama")
        assert llm.backend == "ollama"

    def test_invalid_backend_raises(self):
        with pytest.raises(ValueError, match="Unsupported backend"):
            LLMIntegration(backend="unknown_provider")

    def test_default_model_groq(self):
        llm = LLMIntegration(backend="groq")
        assert llm.model == "llama3-8b-8192"

    def test_default_model_ollama(self):
        llm = LLMIntegration(backend="ollama")
        assert llm.model == "mistral"

    def test_default_model_openai(self):
        llm = LLMIntegration(backend="openai")
        assert llm.model == "gpt-3.5-turbo"

    def test_custom_model(self):
        llm = LLMIntegration(backend="groq", model="llama3-70b-8192")
        assert llm.model == "llama3-70b-8192"


# ── _default_model ─────────────────────────────────────────────────────────────

class TestDefaultModel:
    def test_groq_default(self):
        assert LLMIntegration._default_model("groq") == "llama3-8b-8192"

    def test_ollama_default(self):
        assert LLMIntegration._default_model("ollama") == "mistral"

    def test_unknown_returns_unknown(self):
        assert LLMIntegration._default_model("xyz") == "unknown"


# ── _build_prompt ──────────────────────────────────────────────────────────────

class TestBuildPrompt:
    def setup_method(self):
        self.llm = LLMIntegration()

    def test_contains_func_name(self):
        prompt = self.llm._build_prompt("my_func", "def my_func(): pass", "GOOGLE", "")
        assert "my_func" in prompt

    def test_contains_style(self):
        prompt = self.llm._build_prompt("f", "def f(): pass", "NUMPY", "")
        assert "NUMPY" in prompt

    def test_contains_source(self):
        src = "def f():\n    return 42"
        prompt = self.llm._build_prompt("f", src, "GOOGLE", "")
        assert "return 42" in prompt

    def test_extra_context_included(self):
        prompt = self.llm._build_prompt("f", "def f(): pass", "GOOGLE", "handles auth")
        assert "handles auth" in prompt

    def test_no_extra_context_clean(self):
        prompt = self.llm._build_prompt("f", "def f(): pass", "GOOGLE", "")
        assert "Extra context:" not in prompt


# ── _call_groq (mocked) ───────────────────────────────────────────────────────

class TestCallGroq:
    def test_raises_without_api_key(self, monkeypatch):
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        llm = LLMIntegration(backend="groq")
        with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
            llm._call_groq("test prompt")

    def test_raises_without_groq_package(self, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "fake-key")
        with patch.dict("sys.modules", {"groq": None}):
            llm = LLMIntegration(backend="groq")
            with pytest.raises((RuntimeError, ImportError)):
                llm._call_groq("test prompt")


# ── _call_ollama (mocked) ─────────────────────────────────────────────────────

class TestCallOllama:
    def test_raises_without_ollama_package(self):
        with patch.dict("sys.modules", {"ollama": None}):
            llm = LLMIntegration(backend="ollama")
            with pytest.raises((RuntimeError, ImportError)):
                llm._call_ollama("test prompt")


# ── generate_docstring (mocked backend) ───────────────────────────────────────

class TestGenerateDocstring:
    def test_returns_string(self):
        llm = LLMIntegration(backend="groq")
        with patch.object(llm, "_call_backend", return_value="Mocked docstring."):
            result = llm.generate_docstring("my_func", "def my_func(): pass", "GOOGLE")
        assert isinstance(result, str)
        assert result == "Mocked docstring."

    def test_prompt_built_and_passed(self):
        llm = LLMIntegration(backend="groq")
        with patch.object(llm, "_call_backend", return_value="ok") as mock_call:
            llm.generate_docstring("f", "def f(): pass", "NUMPY")
        mock_call.assert_called_once()
        prompt_arg = mock_call.call_args[0][0]
        assert "NUMPY" in prompt_arg


# ── is_available (mocked) ─────────────────────────────────────────────────────

class TestIsAvailable:
    def test_returns_true_on_success(self):
        llm = LLMIntegration()
        with patch.object(llm, "_call_backend", return_value="pong"):
            assert llm.is_available() is True

    def test_returns_false_on_exception(self):
        llm = LLMIntegration()
        with patch.object(llm, "_call_backend", side_effect=RuntimeError("no connection")):
            assert llm.is_available() is False

import pytest
from unittest.mock import patch, MagicMock
from core.docstring_engine.llm_integration import LLMIntegration


# ── Initialisation ─────────────────────────────────────────────────────────────

class TestInit:
    def test_valid_backend_groq(self):
        llm = LLMIntegration(backend="groq")
        assert llm.backend == "groq"

    def test_valid_backend_ollama(self):
        llm = LLMIntegration(backend="ollama")
        assert llm.backend == "ollama"

    def test_valid_backend_openai(self):
        llm = LLMIntegration(backend="openai")
        assert llm.backend == "openai"

    def test_invalid_backend_raises(self):
        with pytest.raises(ValueError, match="Unsupported backend"):
            LLMIntegration(backend="unknown_backend")

    def test_default_model_groq(self):
        llm = LLMIntegration(backend="groq")
        assert llm.model == "llama3-8b-8192"

    def test_default_model_ollama(self):
        llm = LLMIntegration(backend="ollama")
        assert llm.model == "mistral"

    def test_custom_model(self):
        llm = LLMIntegration(backend="groq", model="my-custom-model")
        assert llm.model == "my-custom-model"


# ── Prompt building ────────────────────────────────────────────────────────────

class TestBuildPrompt:
    def setup_method(self):
        self.llm = LLMIntegration(backend="groq")

    def test_contains_func_name(self):
        prompt = self.llm._build_prompt("my_func", "def my_func(): pass", "GOOGLE", "")
        assert "my_func" in prompt

    def test_contains_style(self):
        prompt = self.llm._build_prompt("f", "def f(): pass", "NUMPY", "")
        assert "NUMPY" in prompt

    def test_contains_source(self):
        src = "def f(): return 42"
        prompt = self.llm._build_prompt("f", src, "GOOGLE", "")
        assert src in prompt

    def test_extra_context_included(self):
        prompt = self.llm._build_prompt("f", "def f(): pass", "GOOGLE", "some context")
        assert "some context" in prompt

    def test_no_extra_context_clean(self):
        prompt = self.llm._build_prompt("f", "def f(): pass", "GOOGLE", "")
        assert "Extra context" not in prompt


# ── Backend dispatch ───────────────────────────────────────────────────────────

class TestCallBackend:
    def test_missing_groq_package_raises(self):
        llm = LLMIntegration(backend="groq")
        with patch.dict("sys.modules", {"groq": None}):
            with pytest.raises(RuntimeError, match="groq package not installed"):
                llm._call_groq("test prompt")

    def test_missing_groq_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        groq_mock = MagicMock()
        with patch.dict("sys.modules", {"groq": groq_mock}):
            llm = LLMIntegration(backend="groq")
            with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
                llm._call_groq("test")

    def test_missing_ollama_package_raises(self):
        llm = LLMIntegration(backend="ollama")
        with patch.dict("sys.modules", {"ollama": None}):
            with pytest.raises(RuntimeError, match="ollama package not installed"):
                llm._call_ollama("test")

    def test_missing_openai_package_raises(self):
        llm = LLMIntegration(backend="openai")
        with patch.dict("sys.modules", {"openai": None}):
            with pytest.raises(RuntimeError, match="openai package not installed"):
                llm._call_openai("test")


# ── is_available ──────────────────────────────────────────────────────────────

class TestIsAvailable:
    def test_returns_false_on_exception(self):
        llm = LLMIntegration(backend="groq")
        with patch.object(llm, "_call_backend", side_effect=RuntimeError("fail")):
            assert llm.is_available() is False

    def test_returns_true_on_success(self):
        llm = LLMIntegration(backend="groq")
        with patch.object(llm, "_call_backend", return_value="ok"):
            assert llm.is_available() is True
