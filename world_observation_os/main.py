#!/usr/bin/env python3
"""World Observation OS — observe the world. Interpret slowly."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.session import get_session_factory, init_db  # noqa: E402
from utils.logger import setup_logger  # noqa: E402


def _parse_signal_ids(raw: str | None) -> list[int] | None:
    if not raw:
        return None
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def cmd_init_db() -> None:
    init_db()
    print("Tables ready: raw_signals, founder_notes, pain_patterns, product_inspirations")


def cmd_observe() -> None:
    from collector.reddit import RedditCollector

    init_db()
    session = get_session_factory()()
    try:
        stats = RedditCollector(session).run()
        print(stats)
    finally:
        session.close()


def cmd_digest() -> None:
    from review.digest import save_digest

    init_db()
    session = get_session_factory()()
    try:
        path = save_digest(session)
        print(f"Digest: {path}")
    finally:
        session.close()


def cmd_review(args: argparse.Namespace) -> None:
    from storage.signals import SignalStore

    init_db()
    session = get_session_factory()()
    try:
        rows = SignalStore(session).list_for_review(limit=args.limit)
        for s in rows:
            tag = ",".join(s.tags or []) or "-"
            print(
                f"#{s.id:5} p={s.review_priority} r/{s.subreddit} {s.source_type:7} "
                f"↑{s.upvotes:4} [{tag}] {(s.title or s.content or '')[:70]}"
            )
    finally:
        session.close()


def cmd_show_signal(args: argparse.Namespace) -> None:
    from storage.signals import SignalStore

    init_db()
    session = get_session_factory()()
    try:
        s = SignalStore(session).get(args.signal_id)
        if not s:
            print("Not found")
            return
        print(f"id={s.id} r/{s.subreddit} {s.source_type} priority={s.review_priority}")
        print(f"url={s.url}")
        print(f"emotion={s.emotion} workaround={s.workaround_detected} tags={s.tags}")
        print("---")
        if s.title:
            print(s.title)
        print(s.content)
    finally:
        session.close()


def cmd_note_add(args: argparse.Namespace) -> None:
    from storage.notes import NoteStore

    init_db()
    session = get_session_factory()()
    try:
        row = NoteStore(session).add({
            "related_signal_ids": _parse_signal_ids(args.signals),
            "note": args.note,
            "resonance_level": args.resonance,
            "observation_type": args.type,
        })
        session.commit()
        print(f"Note #{row.id} saved")
    finally:
        session.close()


def cmd_pattern_add(args: argparse.Namespace) -> None:
    from storage.patterns import PatternStore

    init_db()
    session = get_session_factory()()
    try:
        row = PatternStore(session).add({
            "title": args.title,
            "description": args.description,
            "related_signal_ids": _parse_signal_ids(args.signals),
            "notes": args.notes,
        })
        session.commit()
        print(f"Pattern #{row.id} saved (manual — not auto-generated)")
    finally:
        session.close()


def cmd_pattern_link(args: argparse.Namespace) -> None:
    from storage.patterns import PatternStore

    init_db()
    session = get_session_factory()()
    try:
        p = PatternStore(session).get(args.pattern_id)
        if not p:
            print("Pattern not found")
            return
        existing = list(p.related_signal_ids or [])
        new_ids = _parse_signal_ids(args.signals) or []
        merged = list(dict.fromkeys(existing + new_ids))
        PatternStore(session).update(args.pattern_id, {"related_signal_ids": merged})
        session.commit()
        print(f"Pattern #{args.pattern_id} now links {len(merged)} signal(s)")
    finally:
        session.close()


def cmd_pattern_list() -> None:
    from storage.patterns import PatternStore

    init_db()
    session = get_session_factory()()
    try:
        for p in PatternStore(session).list_all():
            n = len(p.related_signal_ids or [])
            print(f"[{p.id}] {p.title} ({n} signals)")
    finally:
        session.close()


def cmd_inspiration_add(args: argparse.Namespace) -> None:
    from storage.inspirations import InspirationStore

    init_db()
    session = get_session_factory()()
    try:
        row = InspirationStore(session).add({
            "title": args.title,
            "brand_or_product": args.brand,
            "description": args.description,
            "emotional_value_notes": args.emotional,
            "related_signal_ids": _parse_signal_ids(args.signals),
        })
        session.commit()
        print(f"Inspiration #{row.id} saved")
    finally:
        session.close()


def cmd_status() -> None:
    from sqlalchemy import func, select

    from database.models.founder_note import FounderNote
    from database.models.pain_pattern import PainPattern
    from database.models.product_inspiration import ProductInspiration
    from database.models.raw_signal import RawSignal

    init_db()
    session = get_session_factory()()
    try:
        for label, model in [
            ("Signals", RawSignal),
            ("Notes", FounderNote),
            ("Patterns", PainPattern),
            ("Inspirations", ProductInspiration),
        ]:
            n = session.execute(select(func.count()).select_from(model)).scalar()
            print(f"{label:14} {n}")
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="World Observation OS — personal world observation & intuition"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("init-db", "observe", "digest", "status", "pattern-list"):
        sub.add_parser(name)

    rev = sub.add_parser("review", help="Print review queue")
    rev.add_argument("--limit", type=int, default=20)

    show = sub.add_parser("show", help="Show one signal")
    show.add_argument("signal_id", type=int)

    note = sub.add_parser("note-add")
    note.add_argument("--note", required=True)
    note.add_argument("--signals", help="comma-separated signal ids")
    note.add_argument("--resonance", type=int, choices=[1, 2, 3, 4, 5])
    note.add_argument("--type", dest="type", default=None)

    pat = sub.add_parser("pattern-add")
    pat.add_argument("--title", required=True)
    pat.add_argument("--description", default=None)
    pat.add_argument("--signals", default=None)
    pat.add_argument("--notes", default=None)

    link = sub.add_parser("pattern-link")
    link.add_argument("pattern_id", type=int)
    link.add_argument("--signals", required=True)

    insp = sub.add_parser("inspiration-add")
    insp.add_argument("--title", required=True)
    insp.add_argument("--brand", default=None)
    insp.add_argument("--description", default=None)
    insp.add_argument("--emotional", default=None)
    insp.add_argument("--signals", default=None)

    args = parser.parse_args()
    setup_logger()

    with_args = {
        "review", "show", "note-add", "pattern-add", "pattern-link", "inspiration-add"
    }
    handlers = {
        "init-db": cmd_init_db,
        "observe": cmd_observe,
        "digest": cmd_digest,
        "status": cmd_status,
        "review": cmd_review,
        "show": cmd_show_signal,
        "note-add": cmd_note_add,
        "pattern-add": cmd_pattern_add,
        "pattern-link": cmd_pattern_link,
        "pattern-list": cmd_pattern_list,
        "inspiration-add": cmd_inspiration_add,
    }
    h = handlers[args.command]
    h(args) if args.command in with_args else h()


if __name__ == "__main__":
    main()
