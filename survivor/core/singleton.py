"""Single-instance guard. Two bots on one wallet could double-submit orders, so the
second one must refuse to start. Uses an OS file lock, which is released
automatically if the process crashes."""
from __future__ import annotations

import os
from pathlib import Path


class AlreadyRunning(RuntimeError):
    pass


class InstanceLock:
    def __init__(self, path: Path, pid_path: Path | None = None):
        self.path = path
        self.pid_path = pid_path  # plain file other tools can read; the lock file stays locked
        self._fh = None

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fh = open(self.path, "a+")
        try:
            if os.name == "nt":
                import msvcrt

                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            fh.close()
            raise AlreadyRunning(f"another SURVIVOR process holds {self.path}") from e
        self._fh = fh
        if self.pid_path is not None:
            self.pid_path.write_text(str(os.getpid()), encoding="utf-8")

    def release(self) -> None:
        if self._fh is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            self._fh.close()
            self._fh = None
            if self.pid_path is not None:
                self.pid_path.unlink(missing_ok=True)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc):
        self.release()
