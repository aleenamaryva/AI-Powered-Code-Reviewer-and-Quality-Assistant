# examples/sample_b.py
"""Sample Python file B — used for demo and testing of the docstring reviewer."""

import json
import re


def read_file(path):
    with open(path) as f:
        return f.read()


def write_json(data, path):
    """Write data to a JSON file.

    Args:
        data: The data to serialise.
        path (str): Destination file path.
    """
    with open(path, "w") as f:
        json.dump(data, f)


def validate_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def count_words(text: str) -> int:
    """Count the number of words in a string.

    Args:
        text (str): Input text.

    Returns:
        int: Word count.
    """
    return len(text.split())


def reverse_string(s: str) -> str:
    return s[::-1]
