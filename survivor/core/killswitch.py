"""Emergency stop: the bot halts as soon as a KILL file exists in the project root."""
from __future__ import annotations

from pathlib import Path


def kill_requested(kill_file: Path) -> bool:
    return kill_file.exists()
