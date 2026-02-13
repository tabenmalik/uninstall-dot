from __future__ import annotations

import importlib.metadata
import os
import sys
from importlib.metadata import Distribution
from os import PathLike
from pathlib import Path
from types import SimpleNamespace

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


def _dist_origin(dist: Distribution) -> SimpleNamespace | None:
    if sys.version_info >= (3, 13):  # pragma: >=3.13 cover
        return dist.origin
    else:  # pragma: <3.13 cover
        # backport-ish from stdlib
        import json

        text = dist.read_text("direct_url.json")
        origin = None
        if text is not None:
            origin = json.loads(text, object_hook=lambda data: SimpleNamespace(**data))
        return origin


def _dist_package_name(url: str) -> str | None:
    """return package name if a distribution's origin matches the url"""
    for dist in importlib.metadata.distributions():
        origin = _dist_origin(dist)
        if origin is not None and origin.url == url:
            return dist.name
    return None


def _pyproject_package_name(pyproject: PathLike) -> str | None:
    with open(pyproject, mode="rb") as fobj:
        pkg_data = toml_load(fobj)
    return pkg_data.get("project", {}).get("name", None)


def _path_resolve(p: PathLike) -> Path:
    # backporting py3.14 behavior
    return Path(os.path.realpath(p))


def _main():

    cmd = ["pip", *sys.argv[1:]]

    if "uninstall" in cmd and _looks_like_path(cmd[-1]):
        path = _path_resolve(cmd[-1])
        package = _dist_package_name(path.as_uri())

        pyproject = path / "pyproject.toml"
        if not package and pyproject.exists():
            package = _pyproject_package_name(pyproject)

        if package:
            print(
                "pip uninstall does not like directory paths, "
                "but I looked up the project name for you!",
                file=sys.stderr,
            )
            cmd[-1] = package

    return execvp(cmd[0], cmd)
