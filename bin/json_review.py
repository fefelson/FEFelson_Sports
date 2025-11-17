#!/usr/bin/env python3
"""
json_describe.py
----------------
Summarize the structure of a nested JSON file while keeping its shape.

Rules:
- Primitive values → replaced by type name ("int", "str", etc.)
- Dicts → keys preserved and recursed into
- Lists → replaced with a one-element list containing a representative element
          plus a `_meta` field showing list length
"""

import json
import sys
from pathlib import Path
from pprint import pprint


def describe(obj):
    """Recursively describe a JSON structure in-place."""
    # Dicts → recurse on keys
    if isinstance(obj, dict):
        return {k: describe(v) for k, v in obj.items()}

    # Lists → summarize using one representative element
    elif isinstance(obj, list):
        length = len(obj)
        if length == 0:
            return [{"_meta": {"length": 0}}]

        rep = describe(obj[0])  # representative element

        if isinstance(rep, dict):
            rep["_meta"] = {"length": length}
        else:
            rep = {"_meta": {"length": length}, "value": rep}

        return [rep]

    # Primitives → return type name
    else:
        t = type(obj).__name__
        if t == "NoneType":
            return "null"
        return t


def main():
    if len(sys.argv) < 2:
        print("Usage: python json_describe.py <file.json>")
        sys.exit(1)

    path = Path(sys.argv[1])
    with path.open() as f:
        data = json.load(f)

    summary = describe(data)
    pprint(summary)


if __name__ == "__main__":
    main()
