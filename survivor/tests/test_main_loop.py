"""Main loop: heartbeat, KILL file, single instance."""
import json
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from core.config import ROOT, Paths, load_config
from core.main import Bot, main
from core.singleton import AlreadyRunning, InstanceLock


@pytest.fixture
def root(tmp_path):
    shutil.copy(ROOT / "config.json", tmp_path / "config.json")
    return tmp_path


def run_args(root, *extra):
    return ["--root", str(root), "--config", str(root / "config.json"), *extra]


def test_runs_and_writes_heartbeat(root):
    assert main(run_args(root, "--max-ticks", "1")) == 0
    status = json.loads((root / "data" / "status.json").read_text())
    assert status["state"] == "stopped"
    assert status["ticks"] == 1
    assert status["limits"]["max_position_frac"] == 0.15
    assert not (root / "data" / "survivor.pid").exists()  # removed on clean exit


def test_kill_file_stops_before_first_tick(root):
    (root / "KILL").touch()
    assert main(run_args(root)) == 0
    status = json.loads((root / "data" / "status.json").read_text())
    assert status["ticks"] == 0
    assert status["stop_reason"] == "KILL file"


def test_kill_file_stops_running_loop_within_seconds(root):
    paths = Paths.under(root)
    paths.ensure()
    bot = Bot(load_config(root / "config.json"), paths)  # loop_seconds=30 in shipped config
    t = threading.Thread(target=bot.run)
    t.start()
    time.sleep(0.5)
    (root / "KILL").touch()
    t.join(timeout=5)
    assert not t.is_alive()
    assert bot.stop_reason == "KILL file"


def test_tick_exception_does_not_crash(root):
    paths = Paths.under(root)
    paths.ensure()
    bot = Bot(load_config(root / "config.json"), paths)

    def boom():
        bot.ticks += 1
        raise RuntimeError("bad API response")

    bot.tick = boom
    bot.cfg = bot.cfg.__class__(raw=bot.cfg.raw, risk=bot.cfg.risk, loop_seconds=1, mode="idle")
    assert bot.run(max_ticks=2) == 0
    assert bot.errors == 2


def test_second_instance_refused(root):
    lock = InstanceLock(root / "data" / "survivor.lock")
    lock.acquire()
    try:
        with pytest.raises(AlreadyRunning):
            InstanceLock(root / "data" / "survivor.lock").acquire()
        assert main(run_args(root, "--max-ticks", "1")) == 2
    finally:
        lock.release()
    InstanceLock(root / "data" / "survivor.lock").acquire()  # free again after release


def test_runs_as_module_subprocess(root):
    r = subprocess.run(
        [sys.executable, "-m", "core.main", *run_args(root, "--max-ticks", "1")],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, r.stderr
    assert "SURVIVOR stopped" in r.stdout
