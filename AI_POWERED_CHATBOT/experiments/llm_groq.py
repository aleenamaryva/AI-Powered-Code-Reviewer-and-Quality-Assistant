# experiments/llm_groq.py
"""Experiment script — test Groq LLM docstring generation end-to-end."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.docstring_engine.llm_integration import LLMIntegration

SAMPLE_FUNC = '''
def calculate_discount(price: float, rate: float) -> float:
    if rate < 0 or rate > 1:
        raise ValueError("rate must be between 0 and 1")
    return price * (1 - rate)
'''


def run():
    """Run the Groq LLM docstring generation experiment."""
    print("=== Groq LLM Experiment ===")
    try:
        llm = LLMIntegration(backend="groq", model="llama3-8b-8192")
        result = llm.generate_docstring(
            func_name="calculate_discount",
            source=SAMPLE_FUNC,
            style="GOOGLE",
        )
        print("Generated docstring:\n")
        print('"""')
        print(result)
        print('"""')
    except RuntimeError as e:
        print(f"[ERROR] {e}")
        print("Make sure GROQ_API_KEY is set in your .env file.")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run()
