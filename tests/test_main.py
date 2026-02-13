from __future__ import annotations

import shutil
import subprocess
from unittest.mock import MagicMock

import pytest

import uninstall_dot


def test_cli_install():
    assert shutil.which("uninstall-dot") is not None


@pytest.fixture
def project(tmp_path):
    package_dir = tmp_path / "src" / "foobar"
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").touch()

    main_file = package_dir / "__main__.py"
    main_file.write_text("print('hello world!')\n")

    return tmp_path


@pytest.fixture
def uninstall(monkeypatch):
    mock_exec = MagicMock()
    monkeypatch.setattr(uninstall_dot, "execvp", mock_exec)

    def _non_exec_uninstall_dot(cmd):
        monkeypatch.setattr(uninstall_dot.sys, "argv", cmd)
        print(uninstall_dot.sys.argv)
        uninstall_dot._main()
        print(mock_exec.call_args)
        return subprocess.run(mock_exec.call_args[0][1])

    return _non_exec_uninstall_dot


def install(path):
    _ = subprocess.run(["pip", "install", str(path)], check=True)


def test_passthrough(uninstall):
    cp = uninstall(["uninstall_dot", "list"])
    assert cp.returncode == 0
    assert cp.args == ["pip", "list"]


def test_nothing_to_uninstall(project, uninstall):
    assert uninstall(["uninstall_dot", "uninstall", "-y", str(project)]).returncode != 0


def test_toml_project(project, uninstall):
    pyproject = project / "pyproject.toml"
    pyproject.write_text(
        "[build-system]\n"
        'requires = ["setuptools>=61.0"]\n'
        'build-backend = "setuptools.build_meta"\n'
        "\n"
        "[project]\n"
        'name = "fizzbuzz"\n'
        'version = "1.0.0"\n'
    )

    install(project)
    cp = uninstall(["uninstall_dot", "uninstall", "-y", str(project)])
    assert cp.returncode == 0
    assert cp.args[-1] == "fizzbuzz"


def test_invalid_toml(project, uninstall):
    pyproject = project / "pyproject.toml"
    # missing project name!
    pyproject.write_text(
        "[build-system]\n"
        'requires = ["setuptools>=61.0"]\n'
        'build-backend = "setuptools.build_meta"\n'
        "\n"
        "[project]\n"
        'version = "1.0.0"\n'
    )
    cp = uninstall(["uninstall_dot", "uninstall", "-y", str(project)])
    assert cp.returncode != 0
    assert cp.args[-1] == str(project)


def test_setuppy_project(project, uninstall):
    setuppy = project / "setup.py"
    setuppy.write_text(
        "from setuptools import setup\n"
        "\n"
        "setup(name='fizzbuzz', version='1.0.0')\n"
    )

    install(project)
    cp = uninstall(["uninstall_dot", "uninstall", "-y", str(project)])
    assert cp.returncode == 0
    assert cp.args[-1] == "fizzbuzz"
