"""YAML + environment configuration loader."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DEFAULT_SETTINGS_PATH = CONFIG_DIR / "settings.yaml"


def load_settings(path: Path | None = None) -> dict[str, Any]:
    load_dotenv(PROJECT_ROOT / ".env")
    settings_path = path or DEFAULT_SETTINGS_PATH
    with settings_path.open(encoding="utf-8") as f:
        settings = yaml.safe_load(f) or {}
    settings["database_url"] = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://woos:woospass@127.0.0.1:3306/world_observation?charset=utf8mb4",
    )
    reddit_cfg = dict(settings.get("reddit") or {})
    reddit_cfg.update({
        "client_id": os.getenv("REDDIT_CLIENT_ID", ""),
        "client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
        "user_agent": os.getenv(
            "REDDIT_USER_AGENT",
            "world_observation_os/1.0",
        ),
    })
    settings["reddit"] = reddit_cfg
    settings["log_level"] = os.getenv("LOG_LEVEL", "INFO")
    return settings


def get_nested(settings: dict[str, Any], *keys: str, default: Any = None) -> Any:
    node: Any = settings
    for key in keys:
        if not isinstance(node, dict):
            return default
        node = node.get(key)
        if node is None:
            return default
    return node
