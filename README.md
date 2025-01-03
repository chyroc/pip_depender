# pip_depender

[![PyPI version](https://img.shields.io/pypi/v/pip-depender.svg)](https://pypi.org/project/pip-depender/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pip-depender)

Depender: Streamline your Python project dependencies with intelligent version management

## Install

```bash
pip install pip-depender
```

## Usage

```bash
pip-depender <package_name>
```

## Example

```bash
pip-depender httpx


httpx = [
    { version = "^0.28.1", python = ">=3.8" },
    { version = "^0.24.1", python = ">=3.7" },
    { version = "^0.22.0", python = ">=3.6" },
    { version = "^0.0.1", python = ">= 2.7" },
]
```
