import types
import sys
import pathlib
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from xlib.os.os import (
    ProcessPriority,
    get_process_priority,
    set_process_priority,
)


class DummyKernel32:
    class PriorityClass:
        HIGH_PRIORITY_CLASS = 1
        ABOVE_NORMAL_PRIORITY_CLASS = 2
        NORMAL_PRIORITY_CLASS = 3
        BELOW_NORMAL_PRIORITY_CLASS = 4
        IDLE_PRIORITY_CLASS = 5

    def __init__(self, returned_class=PriorityClass.NORMAL_PRIORITY_CLASS):
        self.returned_class = returned_class
        self.set_args = None

    def GetCurrentProcess(self):
        return "proc"

    def GetPriorityClass(self, proc):  # pragma: no cover - mock
        return self.returned_class

    def SetPriorityClass(self, proc, val):  # pragma: no cover - mock
        self.set_args = (proc, val)


@pytest.mark.parametrize(
    "return_val,expected",
    [
        (DummyKernel32.PriorityClass.HIGH_PRIORITY_CLASS, ProcessPriority.HIGH),
        (DummyKernel32.PriorityClass.ABOVE_NORMAL_PRIORITY_CLASS, ProcessPriority.ABOVE_NORMAL),
        (DummyKernel32.PriorityClass.NORMAL_PRIORITY_CLASS, ProcessPriority.NORMAL),
        (DummyKernel32.PriorityClass.BELOW_NORMAL_PRIORITY_CLASS, ProcessPriority.BELOW_NORMAL),
        (DummyKernel32.PriorityClass.IDLE_PRIORITY_CLASS, ProcessPriority.IDLE),
    ],
)
def test_get_process_priority_windows(monkeypatch, return_val, expected):
    import xlib.os.os as osmod

    k32 = DummyKernel32(return_val)
    monkeypatch.setattr(osmod, "kernel32", k32, raising=False)
    monkeypatch.setattr(osmod, "is_win", True)
    monkeypatch.setattr(osmod, "is_linux", False)
    monkeypatch.setattr(osmod, "is_darwin", False)

    assert get_process_priority() == expected


def test_set_process_priority_windows(monkeypatch):
    import xlib.os.os as osmod

    k32 = DummyKernel32()
    monkeypatch.setattr(osmod, "kernel32", k32, raising=False)
    monkeypatch.setattr(osmod, "is_win", True)
    monkeypatch.setattr(osmod, "is_linux", False)
    monkeypatch.setattr(osmod, "is_darwin", False)

    set_process_priority(ProcessPriority.HIGH)

    assert k32.set_args == ("proc", DummyKernel32.PriorityClass.HIGH_PRIORITY_CLASS)


def test_get_process_priority_linux(monkeypatch):
    import xlib.os.os as osmod

    monkeypatch.setattr(osmod, "is_linux", True)
    monkeypatch.setattr(osmod, "is_win", False)
    monkeypatch.setattr(osmod, "is_darwin", False)
    monkeypatch.setattr(osmod, "_niceness", -10)

    assert get_process_priority() == ProcessPriority.ABOVE_NORMAL


def test_set_process_priority_linux(monkeypatch):
    import xlib.os.os as osmod

    calls = {}

    def nice(val):
        calls["val"] = val
        return val

    stub_os = types.SimpleNamespace(nice=nice)
    monkeypatch.setattr(osmod, "os", stub_os)
    monkeypatch.setattr(osmod, "is_linux", True)
    monkeypatch.setattr(osmod, "is_win", False)
    monkeypatch.setattr(osmod, "is_darwin", False)

    set_process_priority(ProcessPriority.ABOVE_NORMAL)

    assert calls["val"] == -10
    assert osmod._niceness == -10


def test_get_process_priority_darwin(monkeypatch):
    import xlib.os.os as osmod

    monkeypatch.setattr(osmod, "is_darwin", True)
    monkeypatch.setattr(osmod, "is_win", False)
    monkeypatch.setattr(osmod, "is_linux", False)
    monkeypatch.setattr(osmod, "_niceness", 5)

    assert get_process_priority() == ProcessPriority.BELOW_NORMAL


def test_set_process_priority_darwin(monkeypatch):
    import xlib.os.os as osmod

    calls = {}

    def nice(val):
        calls["val"] = val
        return val

    stub_os = types.SimpleNamespace(nice=nice)
    monkeypatch.setattr(osmod, "os", stub_os)
    monkeypatch.setattr(osmod, "is_darwin", True)
    monkeypatch.setattr(osmod, "is_win", False)
    monkeypatch.setattr(osmod, "is_linux", False)

    set_process_priority(ProcessPriority.BELOW_NORMAL)

    assert calls["val"] == 5
    assert osmod._niceness == 5
