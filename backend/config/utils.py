import re


def natural_key(s: str):
    """按数值比较其中的数字段：'2-10' 排在 '2-9' 之后。"""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]
