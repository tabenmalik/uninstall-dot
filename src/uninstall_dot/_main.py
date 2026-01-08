from __future__ import annotations

import sys
from typing import NoReturn
from os import execvp
from pathlib import Path
import os
import tomllib

def _looks_like_path(name: str) -> bool:
    return (
        os.path.sep in name
        or (os.path.altsep is not None and os.path.altsep in name)
        or name.startswith(".")
    )


def _get_package_name(pyproject: PathLike) -> str | None:
    with open(pyproject, mode="rb") as fobj:
        pkg_data = tomllib.load(fobj)
        return pkg_data["project"]["name"]


def _main() -> NoReturn:

    cmd = ["pip", *sys.argv[1:]]

    if (
        "uninstall" in cmd
        and _looks_like_path(cmd[-1])
    ):
        pyproject = Path(cmd[-1]) / "pyproject.toml"
        if pyproject.exists():
            package = _get_package_name(pyproject)
            if package:
                cmd[-1] = package


    execvp(cmd[0], cmd)
