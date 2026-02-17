# uninstall-dot

Uninstall local projects by directory.

`uninstall-dot` forwards arguments to pip. If the `uninstall` subcommand is used
with a directory argument then the project name is looked up. Works with any project that includes
[PEP 610](https://peps.python.org/pep-0610/) URL origin in the installed package. If the URL origin
is not available then [PEP 621](https://peps.python.org/pep-0621/) projects can still be uninstalled
by looking up the project name in the pyproject.toml.

## install + setup

```bash
pip install uninstall-dot
alias pip=uninstall-dot
```

## motivation

So often I type `pip install .` that sometimes I mistakenly assume that `pip uninstall .` should
also work. `uninstall-dot` corrects my mistakes and brings symmetry to my life.
