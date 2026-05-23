from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable


def utc_time_label() -> str:
    return datetime.utcnow().strftime("%H:%M:%S")


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def keyword_score(source_text: str, keywords: Iterable[str]) -> tuple[int, list[str]]:
    text = source_text.lower()
    unique_keywords = list(dict.fromkeys(keyword.strip() for keyword in keywords if keyword.strip()))
    if not unique_keywords:
        return 0, []

    matched = [keyword for keyword in unique_keywords if keyword.lower() in text]
    missing = [keyword for keyword in unique_keywords if keyword.lower() not in text]
    score = round((len(matched) / len(unique_keywords)) * 100)
    return score, missing


def clamp(value: int, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, value))
