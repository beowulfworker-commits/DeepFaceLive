import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from xlib.os import os as xos
from xlib.os.os import ProcessPriority

class MockKernel32:
    class PriorityClass:
        HIGH_PRIORITY_CLASS = 1
        ABOVE_NORMAL_PRIORITY_CLASS = 2
        NORMAL_PRIORITY_CLASS = 3
        BELOW_NORMAL_PRIORITY_CLASS = 4
        IDLE_PRIORITY_CLASS = 5

    def GetCurrentProcess(self):
        return None

    def GetPriorityClass(self, process):
        return self.PriorityClass.HIGH_PRIORITY_CLASS

def test_get_process_priority_linux(monkeypatch):
    monkeypatch.setattr(xos, "is_win", False)
    monkeypatch.setattr(xos, "is_darwin", False)
    monkeypatch.setattr(xos, "is_linux", True)
    monkeypatch.setattr(xos, "_niceness", -20)
    assert xos.get_process_priority() is ProcessPriority.HIGH

def test_get_process_priority_darwin(monkeypatch):
    monkeypatch.setattr(xos, "is_win", False)
    monkeypatch.setattr(xos, "is_linux", False)
    monkeypatch.setattr(xos, "is_darwin", True)
    monkeypatch.setattr(xos, "_niceness", -10)
    assert xos.get_process_priority() is ProcessPriority.HIGH

def test_get_process_priority_windows(monkeypatch):
    monkeypatch.setattr(xos, "kernel32", MockKernel32(), raising=False)
    monkeypatch.setattr(xos, "is_win", True)
    monkeypatch.setattr(xos, "is_linux", False)
    monkeypatch.setattr(xos, "is_darwin", False)
    assert xos.get_process_priority() is ProcessPriority.HIGH
