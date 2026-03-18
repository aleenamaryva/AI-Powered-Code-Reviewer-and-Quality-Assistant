# examples/sample_a.py
"""Sample Python file A — used for demo and testing of the docstring reviewer."""


def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)


def find_max(items):
    return max(items)


def format_string(text, width=80):
    return text.center(width)


def greet_user(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"


def flatten_list(nested: list) -> list:
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result
