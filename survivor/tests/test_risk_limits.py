"""Proves the hard risk limits cannot be loosened by config, by the learner, or by bad input."""
import dataclasses
import json
import math

import pytest

from core.config import load_config
from core.risk.limits import (
    HARD,
    HARD_VIEW,
    RiskLimits,
    cap_position_usd,
    can_open_position,
    daily_loss_tripped,
    effective_limits,
)

LOOSE = {
    "max_position_frac": 0.9,
    "max_open_positions": 50,
    "daily_loss_frac": 1.0,
    "daily_loss_pause_hours": 0,
}


def test_hard_values_match_spec():
    assert HARD == RiskLimits(0.15, 3, 0.25, 24)


def test_looser_config_is_clamped_to_hard():
    assert effective_limits(LOOSE) == HARD


def test_stricter_config_is_honoured():
    strict = effective_limits(
        {"max_position_frac": 0.05, "max_open_positions": 1, "daily_loss_frac": 0.1, "daily_loss_pause_hours": 48}
    )
    assert strict == RiskLimits(0.05, 1, 0.1, 48)


@pytest.mark.parametrize("bad", [None, "lots", float("nan"), float("inf"), -1, -0.5, [], {}])
def test_garbage_values_fail_closed(bad):
    lim = effective_limits({k: bad for k in LOOSE})
    assert lim.max_position_frac <= HARD.max_position_frac
    assert lim.max_open_positions <= HARD.max_open_positions
    assert lim.daily_loss_frac <= HARD.daily_loss_frac
    assert lim.daily_loss_pause_hours >= HARD.daily_loss_pause_hours


def test_missing_section_uses_hard():
    assert effective_limits(None) == HARD
    assert effective_limits({}) == HARD


def test_hard_limits_are_immutable():
    with pytest.raises(dataclasses.FrozenInstanceError):
        HARD.max_position_frac = 1.0  # type: ignore[misc]
    with pytest.raises(TypeError):
        HARD_VIEW["max_position_frac"] = 1.0  # type: ignore[index]


def test_position_cap_ignores_forged_limits():
    # Even a RiskLimits object built by hand with huge values cannot exceed the HARD cap.
    forged = RiskLimits(max_position_frac=1.0, max_open_positions=99, daily_loss_frac=1.0, daily_loss_pause_hours=0)
    assert cap_position_usd(100.0, 20.0, forged) == pytest.approx(3.0)
    assert not can_open_position(3, forged)
    assert daily_loss_tripped(20.0, 15.0, forged)  # 25% loss trips even if forged says 100%


@pytest.mark.parametrize(
    "req,eq,expected",
    [(1.0, 20.0, 1.0), (5.0, 20.0, 3.0), (-1, 20, 0.0), (5, 0, 0.0), (5, -10, 0.0), (float("nan"), 20, 0.0), (float("inf"), 20, 0.0)],
)
def test_position_cap(req, eq, expected):
    assert cap_position_usd(req, eq, HARD) == pytest.approx(expected)


def test_open_position_count():
    assert can_open_position(0, HARD)
    assert can_open_position(2, HARD)
    assert not can_open_position(3, HARD)


def test_daily_loss():
    assert not daily_loss_tripped(20.0, 15.01, HARD)
    assert daily_loss_tripped(20.0, 15.0, HARD)
    assert daily_loss_tripped(0.0, 0.0, HARD)          # no baseline: fail closed
    assert daily_loss_tripped(float("nan"), 10, HARD)  # garbage baseline: fail closed


def test_config_file_cannot_loosen(tmp_path):
    cfg = {"run": {"mode": "idle", "loop_seconds": 5}, "risk": LOOSE}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(cfg))
    assert load_config(p).risk == HARD


def test_shipped_config_is_within_hard():
    lim = load_config().risk
    assert lim.max_position_frac <= HARD.max_position_frac
    assert lim.max_open_positions <= HARD.max_open_positions
    assert lim.daily_loss_frac <= HARD.daily_loss_frac
    assert lim.daily_loss_pause_hours >= HARD.daily_loss_pause_hours
    assert math.isfinite(lim.max_position_frac)
