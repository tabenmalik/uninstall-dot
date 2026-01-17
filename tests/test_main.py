from __future__ import annotations

import shutil
from unittest.mock import MagicMock

import pytest

import uninstall_dot


def test_install():
    assert shutil.which("uninstall-dot") is not None


@pytest.mark.parametrize(
    "cmd",
    [
        ("pip", "uninstall", "numpy"),
        ("uninstall-dot", "install", "numpy"),
        ("pip", "help"),
        ("hello", "freeze", "--all"),
    ],
)
def test_passthrough(monkeypatch, cmd):
    mock_exec = MagicMock()
    monkeypatch.setattr(uninstall_dot.sys, "argv", cmd)
    monkeypatch.setattr(uninstall_dot, "execvp", mock_exec)
    uninstall_dot._main()
    assert mock_exec.called
    assert mock_exec.call_args == (("pip", ["pip", *cmd[1:]]),)


def test_uninstall_no_toml(monkeypatch, tmp_path):
    # directory path doesn't get converted to project name without a pyproject.toml
    cmd = ["uninstall-dot", "uninstall", "."]
    mock_exec = MagicMock()
    monkeypatch.setattr(uninstall_dot.sys, "argv", cmd)
    monkeypatch.setattr(uninstall_dot, "execvp", mock_exec)
    monkeypatch.chdir(tmp_path)

    uninstall_dot._main()
    assert mock_exec.called
    assert mock_exec.call_args == (("pip", ["pip", "uninstall", "."]),)


def test_uninstall_with_toml(monkeypatch, tmp_path):
    # look up project name in pyproject.toml
    cmd = ["uninstall-dot", "uninstall", str(tmp_path)]
    mock_exec = MagicMock()
    monkeypatch.setattr(uninstall_dot.sys, "argv", cmd)
    monkeypatch.setattr(uninstall_dot, "execvp", mock_exec)

    with open(tmp_path / "pyproject.toml", mode="wb") as fobj:
        fobj.write(
            b"[build-system]\n"
            b'requires = ["setuptools>=61.0"]\n'
            b'build-backend = "setuptools.build_meta"\n'
            b"\n"
            b"[project]\n"
            b'name = "fizzbuzz"\n'
        )

    uninstall_dot._main()
    assert mock_exec.called
    assert mock_exec.call_args == (("pip", ["pip", "uninstall", "fizzbuzz"]),)


def test_uninstall_toml_but_no_name(monkeypatch, tmp_path):
    # if there's no static project name then continue on like normal
    cmd = ["uninstall-dot", "uninstall", str(tmp_path)]
    mock_exec = MagicMock()
    monkeypatch.setattr(uninstall_dot.sys, "argv", cmd)
    monkeypatch.setattr(uninstall_dot, "execvp", mock_exec)

    with open(tmp_path / "pyproject.toml", mode="wb") as fobj:
        fobj.write(
            b"[build-system]\n"
            b'requires = ["setuptools>=61.0"]\n'
            b'build-backend = "setuptools.build_meta"\n'
        )

    uninstall_dot._main()
    assert mock_exec.called
    assert mock_exec.call_args == (("pip", ["pip", "uninstall", str(tmp_path)]),)
