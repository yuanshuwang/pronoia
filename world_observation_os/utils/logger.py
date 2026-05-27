"""Centralized loguru setup."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from utils.config import PROJECT_ROOT, get_nested, load_settings


def setup_logger(log_level: str | None = None) -> None:
    settings = load_settings()
    level = log_level or settings.get("log_level", "INFO")
    log_dir = PROJECT_ROOT / get_nested(settings, "logging", "dir", default="logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    )
    logger.add(
        log_dir / "world_observation_{time:YYYY-MM-DD}.log",
        level=level,
        rotation=get_nested(settings, "logging", "rotation", default="10 MB"),
        retention=get_nested(settings, "logging", "retention", default="30 days"),
        encoding="utf-8",
    )
