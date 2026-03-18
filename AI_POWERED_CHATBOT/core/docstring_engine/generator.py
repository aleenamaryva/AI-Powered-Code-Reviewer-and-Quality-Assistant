# core/docstring_engine/generator.py
"""Docstring generation engine — builds structured docstrings from function metadata."""

import re

# ── Verb mapping for smart description generation ─────────────────────────────
VERB_MAP = {
    "get": "Retrieves", "fetch": "Fetches", "load": "Loads", "read": "Reads",
    "set": "Sets", "put": "Stores", "save": "Saves", "write": "Writes", "store": "Stores",
    "update": "Updates", "edit": "Edits", "modify": "Modifies", "patch": "Patches",
    "delete": "Deletes", "remove": "Removes", "clear": "Clears", "reset": "Resets",
    "create": "Creates", "make": "Creates", "build": "Builds", "generate": "Generates",
    "add": "Adds", "insert": "Inserts", "append": "Appends", "push": "Appends",
    "check": "Checks", "validate": "Validates", "verify": "Verifies", "is": "Checks if",
    "has": "Checks whether", "can": "Determines whether",
    "find": "Finds", "search": "Searches for", "lookup": "Looks up", "query": "Queries",
    "filter": "Filters", "sort": "Sorts", "parse": "Parses", "decode": "Decodes",
    "encode": "Encodes", "format": "Formats", "render": "Renders", "display": "Displays",
    "show": "Shows", "send": "Sends", "post": "Posts", "upload": "Uploads",
    "download": "Downloads", "export": "Exports", "convert": "Converts",
    "transform": "Transforms", "compute": "Computes", "calculate": "Calculates",
    "process": "Processes", "run": "Runs", "execute": "Executes", "start": "Starts",
    "stop": "Stops", "open": "Opens", "close": "Closes", "connect": "Connects to",
    "log": "Logs", "print": "Prints", "init": "Initializes", "setup": "Sets up",
    "configure": "Configures", "handle": "Handles", "test": "Tests",
    "merge": "Merges", "split": "Splits", "join": "Joins", "combine": "Combines",
    "count": "Counts", "sum": "Computes the sum of", "average": "Calculates the average of",
    "min": "Returns the minimum of", "max": "Returns the maximum of",
    "list": "Lists", "collect": "Collects", "encrypt": "Encrypts", "decrypt": "Decrypts",
    "hash": "Hashes", "draw": "Draws", "plot": "Plots", "resize": "Resizes", "crop": "Crops",
    "notify": "Notifies", "compare": "Compares", "evaluate": "Evaluates",
}


def _words(name: str) -> list:
    """Split a camelCase or snake_case name into lowercase word tokens."""
    name = re.sub(r'([A-Z])', r'_\1', name).lower()
    return [w for w in re.split(r'[_\s]+', name) if w]


def _humanize(name: str) -> str:
    """Convert a snake_case or camelCase name to a human-readable phrase."""
    return " ".join(_words(name))


def smart_description(func_name: str, args: list) -> str:
    """Generate a short human-readable description from function name and args.

    Args:
        func_name (str): The function name.
        args (list): List of argument names.

    Returns:
        str: A generated description sentence.
    """
    words = _words(func_name)
    filtered = [a for a in args if a not in ("self", "cls")]
    if not words:
        return f"Performs the {func_name} operation."
    verb_word, rest = words[0], words[1:]
    verb = VERB_MAP.get(verb_word)
    obj = " ".join(rest) if rest else None
    if verb:
        desc = f"{verb} the {obj}" if obj else (f"{verb} {filtered[0]}" if filtered else f"{verb}s")
    else:
        desc = f"Performs {_humanize(func_name)}"
    desc = desc[0].upper() + desc[1:]
    if not desc.endswith("."):
        desc += "."
    if filtered:
        desc += "\n\nTakes " + ", ".join(f"`{a}`" for a in filtered) + " as input."
    return desc


def build_description(func: dict) -> str:
    """Build a rich natural-language description from parsed function metadata.

    Args:
        func (dict): Function metadata dict with keys: name, args, arg_types,
                     return_type, body_lines.

    Returns:
        str: A descriptive sentence suitable for a docstring summary line.
    """
    name = func["name"]
    args = func["args"]
    arg_types = func.get("arg_types", {})
    return_type = func.get("return_type", "")
    body = " ".join(func.get("body_lines", []))
    filtered = [a for a in args if a not in ("self", "cls")]
    words = _words(name)
    verb_word = words[0] if words else ""
    rest = words[1:]
    verb = VERB_MAP.get(verb_word)
    obj = " ".join(rest) if rest else None

    if verb:
        desc = f"{verb} the {obj}" if obj else (f"{verb} {filtered[0]}" if filtered else f"{verb}s")
    else:
        desc = f"Performs {_humanize(name)}"

    if filtered and arg_types:
        type_counts: dict = {}
        for a in filtered:
            t = arg_types.get(a, "")
            if t:
                type_counts[t] = type_counts.get(t, 0) + 1

        def _article(t):
            return "an" if t[0].lower() in "aeiou" else "a"

        if type_counts:
            parts = []
            for t, count in type_counts.items():
                num_word = {1: "a", 2: "two", 3: "three", 4: "four"}.get(count, str(count))
                parts.append(f"{_article(t)} {t}" if count == 1 else f"{num_word} {t}s")
            type_phrase = " and ".join(parts)
            if verb:
                desc = f"{verb} {type_phrase}" if not obj else f"{verb} the {obj} of {type_phrase}"
            else:
                desc = f"Performs {_humanize(name)} on {type_phrase}"

    if return_type and return_type not in ("None", "none", ""):
        desc += f" and returns a {return_type}"

    body_lower = body.lower()
    if "raise" in body_lower or "raises" in body_lower:
        desc += ". May raise exceptions on invalid input"
    if "open(" in body_lower or "read(" in body_lower or "write(" in body_lower:
        desc += ". Performs file I/O"
    if "request" in body_lower or "http" in body_lower or "urllib" in body_lower:
        desc += ". Makes network requests"

    desc = desc[0].upper() + desc[1:]
    if not desc.endswith("."):
        desc += "."
    return desc


def generate_docstring(func: dict, style: str) -> str:
    """Generate a complete formatted docstring for a given function.

    Args:
        func (dict): Parsed function metadata.
        style (str): Docstring style — one of 'GOOGLE', 'NUMPY', or 'reST'.

    Returns:
        str: A formatted docstring block including quotes.
    """
    name = func["name"]
    args = func["args"]
    arg_types = func.get("arg_types", {})
    return_type = func.get("return_type", "")
    filtered = [a for a in args if a not in ("self", "cls")]
    summary = build_description(func)

    def _ret_type():
        return return_type if return_type else _humanize(name)

    if style == "GOOGLE":
        lines = ['"""', summary, ""]
        if filtered:
            lines += ["Args:"]
            for a in filtered:
                t = arg_types.get(a, "")
                lines.append(f"    {a}{' (' + t + ')' if t else ''}: The {_humanize(a)} value.")
        lines += ["", "Returns:", f"    {_ret_type()}: Result of {_humanize(name)}.", '"""']

    elif style == "NUMPY":
        lines = ['"""', summary, "", "Parameters", "----------"]
        for a in filtered:
            t = arg_types.get(a, "any")
            lines += [f"{a} : {t}", f"    The {_humanize(a)} value."]
        lines += ["", "Returns", "-------",
                  return_type if return_type else "any",
                  f"    Result of {_humanize(name)}.", '"""']

    else:  # reST
        lines = ['"""', summary, ""]
        for a in filtered:
            t = arg_types.get(a, "")
            lines.append(f":param {a}: The {_humanize(a)} value.")
            if t:
                lines.append(f":type {a}: {t}")
        if return_type:
            lines.append(f":rtype: {return_type}")
        lines += [f":returns: Result of {_humanize(name)}.", '"""']

    return "\n".join(lines)
