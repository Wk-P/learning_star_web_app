import re


def natural_key(s: str):
    """Sort key that orders numeric substrings by value: '2-10' > '2-9'."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]
