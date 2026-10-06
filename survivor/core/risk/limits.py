"""Hard risk limits. LOCKED: the learning engine and config.json can only tighten these.

Anything that sizes or opens a position must go through `effective_limits()` and
`cap_position_usd()`. Values in config.json that are looser than HARD are ignored
(clamped), never honoured.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class RiskLimits:
    max_position_frac: float      # max share of equity in a single new position
    max_open_positions: int       # max concurrent open positions
    daily_loss_frac: float        # realised + unrealised loss in a UTC day that triggers a pause
    daily_loss_pause_hours: int   # minimum pause after the daily loss limit trips


HARD = RiskLimits(
    max_position_frac=0.15,
    max_open_positions=3,
    daily_loss_frac=0.25,
    daily_loss_pause_hours=24,
)

# Read-only view for anything that wants to display the limits.
HARD_VIEW: Mapping[str, float] = MappingProxyType(
    {
        "max_position_frac": HARD.max_position_frac,
        "max_open_positions": HARD.max_open_positions,
        "daily_loss_frac": HARD.daily_loss_frac,
        "daily_loss_pause_hours": HARD.daily_loss_pause_hours,
    }
)


def _finite_or(value, fallback: float) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return fallback
    return v if math.isfinite(v) else fallback


def effective_limits(requested: Mapping | None) -> RiskLimits:
    """Merge requested limits with HARD, keeping whichever is stricter.

    Invalid, missing, negative or non-finite values fall back to the HARD value.
    The pause is the one limit where *longer* is stricter.
    """
    r = dict(requested or {})

    frac = _finite_or(r.get("max_position_frac"), HARD.max_position_frac)
    frac = min(max(frac, 0.0), HARD.max_position_frac)

    n_open = _finite_or(r.get("max_open_positions"), HARD.max_open_positions)
    n_open = int(min(max(math.floor(n_open), 0), HARD.max_open_positions))

    loss = _finite_or(r.get("daily_loss_frac"), HARD.daily_loss_frac)
    loss = min(max(loss, 0.0), HARD.daily_loss_frac)

    pause = _finite_or(r.get("daily_loss_pause_hours"), HARD.daily_loss_pause_hours)
    pause = int(max(math.ceil(pause), HARD.daily_loss_pause_hours))

    return RiskLimits(frac, n_open, loss, pause)


def cap_position_usd(requested_usd: float, equity_usd: float, limits: RiskLimits) -> float:
    """Clamp a proposed position size to the per-trade cap. Never returns more than
    HARD.max_position_frac * equity, whatever `limits` says."""
    req = _finite_or(requested_usd, 0.0)
    eq = _finite_or(equity_usd, 0.0)
    if req <= 0 or eq <= 0:
        return 0.0
    frac = min(limits.max_position_frac, HARD.max_position_frac)
    return min(req, eq * frac)


def can_open_position(open_positions: int, limits: RiskLimits) -> bool:
    cap = min(limits.max_open_positions, HARD.max_open_positions)
    return open_positions < cap


def daily_loss_tripped(day_start_equity: float, current_equity: float, limits: RiskLimits) -> bool:
    start = _finite_or(day_start_equity, 0.0)
    now = _finite_or(current_equity, 0.0)
    if start <= 0:
        return True  # no sane baseline: fail closed
    frac = min(limits.daily_loss_frac, HARD.daily_loss_frac)
    return (start - now) / start >= frac
