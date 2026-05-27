"""Reddit community observation — record reality, minimal interpretation."""

from __future__ import annotations

import time
from datetime import datetime, timezone

import praw
from loguru import logger
from praw.models import Comment, Submission
from sqlalchemy.orm import Session

from heuristics.enrich import enrich_signal, passes_minimum_bar
from storage.signals import SignalStore
from utils.config import get_nested, load_settings


class RedditCollector:
    def __init__(self, session: Session):
        self.session = session
        self.store = SignalStore(session)
        settings = load_settings()
        self.cfg = get_nested(settings, "reddit", default={})
        retry = self.cfg.get("retry", {})
        self.max_attempts = retry.get("max_attempts", 3)
        self.delay = retry.get("delay_seconds", 2)
        self._reddit = self._client(settings)

    def _client(self, settings: dict) -> praw.Reddit:
        creds = settings["reddit"]
        if not creds.get("client_id") or not creds.get("client_secret"):
            raise ValueError("Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env")
        return praw.Reddit(
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            user_agent=creds["user_agent"],
        )

    def run(self) -> dict:
        stats = {"new": 0, "updated": 0, "skipped": 0}
        for name in self.cfg.get("subreddits", []):
            logger.info(f"Observing r/{name}")
            self._observe_subreddit(name, stats)
        self.session.commit()
        logger.info(f"Observation round complete: {stats}")
        return stats

    def _observe_subreddit(self, name: str, stats: dict) -> None:
        sub = self._retry(lambda: self._reddit.subreddit(name), f"r/{name}")
        limit = self.cfg.get("posts_per_subreddit", 15)
        sort = self.cfg.get("sort", "new")

        def fetch():
            if sort == "hot":
                return list(sub.hot(limit=limit))
            return list(sub.new(limit=limit))

        for submission in self._retry(fetch, f"posts r/{name}"):
            self._save_post(submission, name, stats)
            self._save_comments(submission, name, stats)

    def _save_post(self, sub: Submission, subreddit: str, stats: dict) -> None:
        body = (sub.title or "") + "\n" + (sub.selftext or "")
        if not passes_minimum_bar(body, "post", sub.score):
            stats["skipped"] += 1
            return

        hints = enrich_signal(body, "post", sub.score)
        created = datetime.fromtimestamp(sub.created_utc, tz=timezone.utc).replace(tzinfo=None)
        data = {
            "source_platform": "reddit",
            "subreddit": subreddit,
            "source_type": "post",
            "external_id": sub.id,
            "post_id": sub.id,
            "author": str(sub.author) if sub.author else None,
            "title": sub.title,
            "content": sub.selftext or sub.title,
            "url": f"https://reddit.com{sub.permalink}",
            "created_at": created,
            "upvotes": sub.score,
            "comment_count": sub.num_comments,
            "language": "en",
            "raw_json": {
                "is_self": sub.is_self,
                "link_flair": sub.link_flair_text,
            },
            **hints,
        }
        _, created_flag = self.store.upsert(data)
        if created_flag:
            stats["new"] += 1
        else:
            stats["updated"] += 1

    def _save_comments(self, sub: Submission, subreddit: str, stats: dict) -> None:
        limit = self.cfg.get("comments_per_post", 20)

        def expand():
            sub.comments.replace_more(limit=0)
            return sub.comments.list()[:limit]

        for item in self._retry(expand, f"comments {sub.id}"):
            if not isinstance(item, Comment):
                continue
            body = item.body or ""
            if not passes_minimum_bar(body, "comment", item.score):
                stats["skipped"] += 1
                continue

            hints = enrich_signal(body, "comment", item.score)
            created = datetime.fromtimestamp(item.created_utc, tz=timezone.utc).replace(
                tzinfo=None
            )
            data = {
                "source_platform": "reddit",
                "subreddit": subreddit,
                "source_type": "comment",
                "external_id": item.id,
                "post_id": sub.id,
                "author": str(item.author) if item.author else None,
                "title": None,
                "content": body,
                "url": f"https://reddit.com{sub.permalink}",
                "created_at": created,
                "upvotes": item.score,
                "comment_count": 0,
                "language": "en",
                "raw_json": {"parent_id": item.parent_id},
                **hints,
            }
            _, created_flag = self.store.upsert(data)
            if created_flag:
                stats["new"] += 1
            else:
                stats["updated"] += 1

    def _retry(self, fn, label: str):
        last = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return fn()
            except Exception as exc:
                last = exc
                logger.warning(f"{label} failed ({attempt}/{self.max_attempts}): {exc}")
                if attempt < self.max_attempts:
                    time.sleep(self.delay * attempt)
        raise last
