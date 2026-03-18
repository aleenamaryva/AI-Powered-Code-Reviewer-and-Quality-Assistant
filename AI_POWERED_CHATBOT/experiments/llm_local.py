# experiments/llm_local.py
"""Experiment script — test local Ollama LLM docstring generation end-to-end."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.docstring_engine.llm_integration import LLMIntegration

SAMPLE_FUNC = '''
def merge_dicts(*dicts: dict) -> dict:
    result = {}
    for d in dicts:
        result.update(d)
    return result
'''


def run():
    """Run the local Ollama LLM docstring generation experiment."""
    print("=== Local Ollama LLM Experiment ===")
    print("Requires: ollama running locally with 'mistral' model pulled.")
    print("Run: ollama pull mistral && ollama serve\n")
    try:
        llm = LLMIntegration(backend="ollama", model="mistral")
        result = llm.generate_docstring(
            func_name="merge_dicts",
            source=SAMPLE_FUNC,
            style="NUMPY",
        )
        print("Generated docstring (NUMPY style):\n")
        print('"""')
        print(result)
        print('"""')
    except RuntimeError as e:
        print(f"[ERROR] {e}")
        print("Make sure Ollama is running: `ollama serve`")


if __name__ == "__main__":
    run()
