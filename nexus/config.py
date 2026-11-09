"""Configuration helpers; secrets are read from environment or Streamlit secrets."""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"


def get_setting(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass
    return default


def database_url() -> str:
    return get_setting("NEXUS_DATABASE_URL", f"sqlite:///{DATA_DIR / 'nexus_demo.db'}") or f"sqlite:///{DATA_DIR / 'nexus_demo.db'}"


def app_mode() -> str:
    return get_setting("NEXUS_APP_MODE", "demo") or "demo"
