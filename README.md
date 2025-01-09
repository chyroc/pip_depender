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

When you add some dependencies to your project, But this package is not compatible with your python version, you may got some error like this:

```bash
poetry add websockets
Using version ^14.1 for websockets

Updating dependencies
Resolving dependencies... (0.0s)

The current project's supported Python range (>=3.8,<4.0) is not compatible with some of the required packages Python requirement:
  - websockets requires Python >=3.9, so it will not be satisfied for Python >=3.8,<3.9

Because no versions of websockets match >14.1,<15.0
 and websockets (14.1) requires Python >=3.9, websockets is forbidden.
So, because pip-depender depends on websockets (^14.1), version solving failed.

  • Check your dependencies Python requirement: The Python requirement can be specified via the `python` or `markers` properties

    For websockets, a possible solution would be to set the `python` property to ">=3.9,<4.0"

    https://python-poetry.org/docs/dependency-specification/#python-restricted-dependencies,
    https://python-poetry.org/docs/dependency-specification/#using-environment-markers
```

You can use `pip-depender` to find the compatible version of the package.

```bash
pip-depender websockets

Fetching package info...  [██████████░░░░░░░░░░░░░░░░░░░░░░░░░░]   30%  00:00:02
📦 Package Info:
  • Name: websockets
  • Description: An implementation of the WebSocket Protocol (RFC 6455 & 7692)
  • Total Versions: 44

Analyzing version compatibility...  [████████████████████████████████████]  100%

🎯 Recommended Version(s):
websockets = [
    { version = "^14.1.0", python = ">=3.9" },
    { version = "^13.1.0", python = ">=3.8,<3.9" },
    { version = "^11.0.3", python = ">=3.7,<3.8" },
    { version = "^9.1.0", python = ">=3.6.1,<3.7" },
    { version = "^8.0.2", python = ">=3.6,<3.6.1" },
    { version = "^7.0.0", python = ">=3.4,<3.6" },
    { version = "^5.0.1", python = ">=2.7,<3.4" },
]
```
