from __future__ import annotations

import os
import sys
from os import PathLike
from pathlib import Path

if sys.version_info >= (3, 11):  # pragma: >=3.11 cover
    from tomllib import load as toml_load
else:  # pragma: <3.11 cover
    from tomli import load as toml_load


if sys.platform == "win32":  # pragma: win32 cover
    import subprocess

    def execvp(file: str, args: list[str], /) -> int:
        return subprocess.run(args).returncode

else:  # pragma: win32 no cover
    from os import execvp


def _looks_like_path(name: str) -> bool:
    return (
        os.path.sep in name
        or (os.path.altsep is not None and os.path.altsep in name)
        or name.startswith(".")
    )


def _get_package_name(pyproject: PathLike) -> str | None:
    with open(pyproject, mode="rb") as fobj:
        pkg_data = toml_load(fobj)
    return pkg_data.get("project", {}).get("name", None)


def _main():

    cmd = ["pip", *sys.argv[1:]]

    if "uninstall" in cmd and _looks_like_path(cmd[-1]):
        pyproject = Path(cmd[-1]) / "pyproject.toml"
        if pyproject.exists():
            package = _get_package_name(pyproject)
            if package:
                print(
                    "pip uninstall does not like directory paths, "
                    "but I looked up the project name for you!",
                    file=sys.stderr,
                )
                cmd[-1] = package

    return execvp(cmd[0], cmd)
