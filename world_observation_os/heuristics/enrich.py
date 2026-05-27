"""Lightweight heuristics — assist reading, not conclusions."""

from __future__ import annotations

from utils.config import get_nested, load_settings


def enrich_signal(text: str, source_type: str, upvotes: int = 0) -> dict:
    """
    Returns optional hints: emotion, workaround_detected, tags, review_priority.
    Priority is a soft queue hint (0-10), NOT business scoring.
    """
    settings = load_settings()
    cfg = get_nested(settings, "filters", default={})
    lower = (text or "").lower()
    length = len(text or "")

    emotional = cfg.get("emotional_markers", [])
    workaround = cfg.get("workaround_markers", [])

    tags: list[str] = []
    emotion: str | None = None
    workaround_detected = False

    for marker in emotional:
        if marker.lower() in lower:
            tags.append(f"emotion:{marker}")
            if not emotion:
                emotion = marker

    for marker in workaround:
        if marker.lower() in lower:
            workaround_detected = True
            tags.append("workaround")

    if source_type == "post" and length >= cfg.get("min_post_chars", 120):
        tags.append("long_form")
    if source_type == "comment" and length >= cfg.get("min_comment_chars", 80):
        tags.append("long_form")

    priority = 0
    if workaround_detected:
        priority += 3
    if emotion:
        priority += 2
    if "long_form" in tags:
        priority += 2
    if upvotes >= 10:
        priority += 1
    if upvotes >= 50:
        priority += 1

    return {
        "emotion": emotion,
        "workaround_detected": workaround_detected,
        "tags": tags or None,
        "review_priority": min(priority, 10),
    }


def passes_minimum_bar(
    text: str,
    source_type: str,
    upvotes: int,
) -> bool:
    """Skip very low-signal noise — still conservative."""
    settings = load_settings()
    cfg = get_nested(settings, "filters", default={})
    text = text or ""
    min_chars = (
        cfg.get("min_post_chars", 120)
        if source_type == "post"
        else cfg.get("min_comment_chars", 80)
    )
    min_votes = (
        cfg.get("min_upvotes_post", 0)
        if source_type == "post"
        else cfg.get("min_upvotes_comment", 1)
    )

    hints = enrich_signal(text, source_type, upvotes)
    # Keep if long, emotional, workaround, or already popular
    if len(text) >= min_chars:
        return True
    if hints["emotion"] or hints["workaround_detected"]:
        return True
    if upvotes >= max(min_votes, 5):
        return True
    return False
