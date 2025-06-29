from __future__ import annotations

import re


def to_snake_case(word: str) -> str:
    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", word)
    word = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", word)
    word = word.replace("-", "_")
    return word.lower()


def to_pascale_case(word: str) -> str:
    return re.sub(r"(^|_)([a-z])", lambda match: match.group(2).upper(), word)
