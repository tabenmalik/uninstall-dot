import shutil

from uninstall_dot._main import _main

def test_install():
    assert shutil.which("uninstall-dot") is not None
