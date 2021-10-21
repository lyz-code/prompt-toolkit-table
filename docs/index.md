[![Actions Status](https://github.com/lyz-code/prompt-toolkit-table/workflows/Tests/badge.svg)](https://github.com/lyz-code/prompt-toolkit-table/actions)
[![Actions Status](https://github.com/lyz-code/prompt-toolkit-table/workflows/Build/badge.svg)](https://github.com/lyz-code/prompt-toolkit-table/actions)
[![Coverage Status](https://coveralls.io/repos/github/lyz-code/prompt-toolkit-table/badge.svg?branch=master)](https://coveralls.io/github/lyz-code/prompt-toolkit-table?branch=master)

Table implementation for the Python Prompt Toolkit library

# Installing

```bash
pip install prompt-toolkit-table
```

# A Simple Example

```python
{! examples/simple-example.py !} # noqa
```

# References

As most open sourced programs, `prompt-toolkit-table` is standing on the shoulders of
giants, namely:

[Pytest](https://docs.pytest.org/en/latest)
: Testing framework, enhanced by the awesome
    [pytest-cases](https://smarie.github.io/python-pytest-cases/) library that made
    the parametrization of the tests a lovely experience.

[Mypy](https://mypy.readthedocs.io/en/stable/)
: Python static type checker.

[Flakehell](https://github.com/life4/flakehell)
: Python linter with [lots of
    checks](https://lyz-code.github.io/blue-book/devops/flakehell/#plugins).

[Black](https://black.readthedocs.io/en/stable/)
: Python formatter to keep a nice style without effort.

[Autoimport](https://github.com/lyz-code/autoimport)
: Python formatter to automatically fix wrong import statements.

[isort](https://github.com/timothycrosley/isort)
: Python formatter to order the import statements.

[Pip-tools](https://github.com/jazzband/pip-tools)
: Command line tool to manage the dependencies.

[Mkdocs](https://www.mkdocs.org/)
: To build this documentation site, with the
[Material theme](https://squidfunk.github.io/mkdocs-material).

[Safety](https://github.com/pyupio/safety)
: To check the installed dependencies for known security vulnerabilities.

[Bandit](https://bandit.readthedocs.io/en/latest/)
: To finds common security issues in Python code.

[Yamlfix](https://github.com/lyz-code/yamlfix)
: YAML fixer.

# Contributing

For guidance on setting up a development environment, and how to make
a contribution to *prompt-toolkit-table*, see [Contributing to
prompt-toolkit-table](https://lyz-code.github.io/prompt-toolkit-table/contributing).
