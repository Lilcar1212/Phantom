"""SURVIVOR main loop.

Milestone 1: the loop runs, honours the KILL file and signals, writes a heartbeat
to data/status.json, and refuses to start twice. Trading arrives in milestone 2.
"""
from __future__ import annotations

import argparse
import json
import logging
import logging.handlers
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import ROOT, Config, Paths, load_config
from .killswitch import kill_requested
from .singleton import AlreadyRunning, InstanceLock

log = logging.getLogger("survivor")


def setup_logging(paths: Paths) -> None:
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    fh = logging.handlers.RotatingFileHandler(
        paths.logs / "survivor.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8"
    )
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    root = logging.getLogger()
    root.handlers[:] = [fh, sh]
    root.setLevel(logging.INFO)


def write_status(paths: Paths, **fields) -> None:
    """Atomic write so status.ps1 and the dashboard never read a half-written file."""
    payload = {"pid": os.getpid(), "updated_utc": datetime.now(timezone.utc).isoformat(), **fields}
    tmp = paths.status_file.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, paths.status_file)


class Bot:
    def __init__(self, cfg: Config, paths: Paths):
        self.cfg = cfg
        self.paths = paths
        self.stop_reason: str | None = None
        self.started = time.time()
        self.ticks = 0
        self.errors = 0

    def request_stop(self, reason: str) -> None:
        if self.stop_reason is None:
            self.stop_reason = reason
            log.info("stop requested: %s", reason)

    def tick(self) -> None:
        # Milestone 2+: refresh balances, screen tokens, evaluate strategies, manage positions.
        self.ticks += 1

    def heartbeat(self, state: str) -> None:
        write_status(
            self.paths,
            state=state,
            mode=self.cfg.mode,
            ticks=self.ticks,
            errors=self.errors,
            uptime_s=round(time.time() - self.started, 1),
            stop_reason=self.stop_reason,
            limits=self.cfg.risk.__dict__,
        )

    def sleep_until_next(self) -> None:
        deadline = time.monotonic() + self.cfg.loop_seconds
        while time.monotonic() < deadline and self.stop_reason is None:
            if kill_requested(self.paths.kill_file):
                self.request_stop("KILL file")
                return
            time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))

    def run(self, max_ticks: int | None = None) -> int:
        log.info("SURVIVOR starting: mode=%s limits=%s", self.cfg.mode, self.cfg.risk)
        while self.stop_reason is None:
            if kill_requested(self.paths.kill_file):
                self.request_stop("KILL file")
                break
            try:
                self.tick()
            except Exception:
                # Keep running: one bad API response must not take the bot down.
                self.errors += 1
                log.exception("tick failed (errors so far: %d)", self.errors)
            self.heartbeat("running")
            if max_ticks is not None and self.ticks >= max_ticks:
                self.request_stop("max_ticks reached")
                break
            self.sleep_until_next()
        self.heartbeat("stopped")
        log.info("SURVIVOR stopped: %s", self.stop_reason)
        return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="survivor")
    ap.add_argument("--config", type=Path, default=ROOT / "config.json")
    ap.add_argument("--root", type=Path, default=ROOT, help="project root holding data/ and KILL")
    ap.add_argument("--max-ticks", type=int, default=None, help="exit after N loops (tests)")
    args = ap.parse_args(argv)

    paths = Paths.under(args.root)
    paths.ensure()
    setup_logging(paths)
    cfg = load_config(args.config)

    try:
        lock = InstanceLock(paths.lock_file, paths.pid_file)
        lock.acquire()
    except AlreadyRunning as e:
        log.error("%s; refusing to start a second copy", e)
        return 2

    bot = Bot(cfg, paths)
    signal.signal(signal.SIGINT, lambda *_: bot.request_stop("SIGINT"))
    signal.signal(signal.SIGTERM, lambda *_: bot.request_stop("SIGTERM"))
    if hasattr(signal, "SIGBREAK"):  # Windows Ctrl+Break
        signal.signal(signal.SIGBREAK, lambda *_: bot.request_stop("SIGBREAK"))
    try:
        return bot.run(max_ticks=args.max_ticks)
    finally:
        lock.release()


if __name__ == "__main__":
    sys.exit(main())
