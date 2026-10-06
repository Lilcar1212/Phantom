"""Load config.json and resolve paths. Risk values are clamped by core.risk.limits."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .risk.limits import RiskLimits, effective_limits

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Paths:
    root: Path
    data: Path
    logs: Path
    reports: Path
    kill_file: Path
    status_file: Path
    pid_file: Path
    lock_file: Path
    ledger_db: Path

    @classmethod
    def under(cls, root: Path) -> "Paths":
        data = root / "data"
        return cls(
            root=root,
            data=data,
            logs=data / "logs",
            reports=root / "reports",
            kill_file=root / "KILL",
            status_file=data / "status.json",
            pid_file=data / "survivor.pid",
            lock_file=data / "survivor.lock",
            ledger_db=data / "ledger.sqlite",
        )

    def ensure(self) -> None:
        for p in (self.data, self.logs, self.reports):
            p.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Config:
    raw: dict
    risk: RiskLimits
    loop_seconds: float
    mode: str


VALID_MODES = ("idle", "shadow", "live")


def load_config(path: Path | None = None) -> Config:
    path = path or ROOT / "config.json"
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    run = raw.get("run", {})
    mode = run.get("mode", "idle")
    if mode not in VALID_MODES:
        raise ValueError(f"run.mode must be one of {VALID_MODES}, got {mode!r}")
    loop = float(run.get("loop_seconds", 30))
    if not 1 <= loop <= 3600:
        raise ValueError("run.loop_seconds must be between 1 and 3600")
    return Config(raw=raw, risk=effective_limits(raw.get("risk")), loop_seconds=loop, mode=mode)
