"""Daily observation digest — reading aid, not business conclusions."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from database.models.raw_signal import RawSignal
from storage.notes import NoteStore
from storage.patterns import PatternStore
from storage.signals import SignalStore
from utils.config import PROJECT_ROOT, get_nested, load_settings


def build_digest(session: Session) -> str:
    settings = load_settings()
    review_cfg = get_nested(settings, "review", default={})
    top_n = review_cfg.get("digest_top_n", 25)

    signals = SignalStore(session).list_for_review(limit=top_n, min_priority=1)
    if not signals:
        signals = SignalStore(session).list_recent(limit=top_n)

    patterns = PatternStore(session).list_all()
    notes = NoteStore(session).list_recent(limit=10)

    today = datetime.utcnow().strftime("%Y-%m-%d")
    lines = [
        "# Observation Digest",
        "",
        f"**Date:** {today} UTC",
        "",
        "> Observe first. Interpret slowly. No scores, no rankings — just material to read.",
        "",
        "---",
        "",
        "## Worth reading today",
        "",
    ]

    if not signals:
        lines.append("_No signals yet. Run `python main.py observe`._\n")
    else:
        for s in signals:
            lines.append(_format_signal(s))
        lines.append("")

    lines.extend(["---", "", "## Your pain patterns (manual)", ""])
    if not patterns:
        lines.append("_None yet. Add with `pattern-add` when something recurs over weeks._\n")
    else:
        for p in patterns[:15]:
            ids = p.related_signal_ids or []
            lines.append(f"- **{p.title}** — {len(ids)} linked signal(s)")
            if p.description:
                lines.append(f"  {p.description[:200]}")
        lines.append("")

    lines.extend(["---", "", "## Recent founder notes", ""])
    if not notes:
        lines.append("_No notes yet. Use `note-add` after reading._\n")
    else:
        for n in notes:
            lines.append(f"- ({n.resonance_level or '?'}/5) {n.note[:300]}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Reminder",
        "",
        "This digest organizes reading. It does not validate startups or predict markets.",
        "",
    ])

    return "\n".join(lines)


def _format_signal(s: RawSignal) -> str:
    header = f"### r/{s.subreddit} · {s.source_type} · priority {s.review_priority}"
    meta = []
    if s.emotion:
        meta.append(f"emotion: {s.emotion}")
    if s.workaround_detected:
        meta.append("workaround")
    if s.tags:
        meta.append(", ".join(s.tags[:5]))
    meta_line = f"*{' · '.join(meta)}* · ↑{s.upvotes}" if meta else f"*↑{s.upvotes}*"

    title = s.title or (s.content[:80] + "..." if s.content else "")
    link = f"[read]({s.url})" if s.url else ""
    body = (s.content or "")[:500]
    if len(s.content or "") > 500:
        body += "…"

    return "\n".join([
        header,
        meta_line,
        f"**{title}** {link}  · signal `#{s.id}`",
        "",
        f"> {body}",
        "",
    ])


def save_digest(session: Session) -> str:
    content = build_digest(session)
    settings = load_settings()
    out_dir = PROJECT_ROOT / get_nested(settings, "review", "digest_dir", default="output/digests")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"digest_{datetime.utcnow().strftime('%Y-%m-%d')}.md"
    path.write_text(content, encoding="utf-8")
    return str(path)
