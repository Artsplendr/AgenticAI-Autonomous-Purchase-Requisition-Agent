"""Lightweight policy retriever over markdown files."""

import re
from pathlib import Path


POLICY_DIR = Path(__file__).parents[1] / 'data' / 'policies'


def retrieve_policy(query: str) -> list[str]:
    query_terms = _normalize_terms(query)
    scored_snippets: list[tuple[int, str]] = []
    fallback_snippets: list[str] = []

    for path in POLICY_DIR.glob('*.md'):
        text = path.read_text() if path.exists() else ''
        for line in text.splitlines():
            cleaned = line.strip()
            if not cleaned or cleaned.startswith('#'):
                continue
            score = _score_line(cleaned, query_terms)
            if score > 0:
                scored_snippets.append((score, f"{path.stem}: {cleaned}"))
            elif cleaned.startswith('-') and len(fallback_snippets) < 8:
                fallback_snippets.append(f"{path.stem}: {cleaned}")

    if scored_snippets:
        scored_snippets.sort(key=lambda row: row[0], reverse=True)
        deduped: list[str] = []
        for _, snippet in scored_snippets:
            if snippet not in deduped:
                deduped.append(snippet)
            if len(deduped) >= 6:
                break
        return deduped

    return fallback_snippets[:6]


def _normalize_terms(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9\-]+", text.lower())
    base = [token for token in tokens if len(token) > 2]
    expansions = set(base)
    synonym_map = {
        "laptop": {"it", "hardware", "device"},
        "desk": {"furniture", "office"},
        "usb-c": {"accessories", "cable"},
        "urgent": {"expedite", "priority"},
        "engineering": {"r&d", "technology"},
        "operations": {"ops"},
    }
    for token in base:
        expansions.update(synonym_map.get(token, set()))
    return sorted(expansions)


def _score_line(line: str, query_terms: list[str]) -> int:
    lowered = line.lower()
    score = 0
    for term in query_terms:
        if term in lowered:
            score += 1
    # Prioritize policy bullets that mention must/not/require.
    if any(keyword in lowered for keyword in ("must", "required", "prohibited", "forbidden", "threshold")):
        score += 1
    return score
