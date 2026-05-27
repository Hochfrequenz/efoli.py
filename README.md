# E-Foli

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python Versions (officially) supported](https://img.shields.io/pypi/pyversions/efoli.svg)
![Pypi status badge](https://img.shields.io/pypi/v/efoli)
![Unittests status badge](https://github.com/Hochfrequenz/efoli/workflows/Unittests/badge.svg)
![Coverage status badge](https://github.com/Hochfrequenz/efoli/workflows/Coverage/badge.svg)
![Linting status badge](https://github.com/Hochfrequenz/efoli/workflows/Linting/badge.svg)
![Black status badge](https://github.com/Hochfrequenz/efoli/workflows/Formatting/badge.svg)

`efoli` is a Python package, that contains
- an Enum `EdifactFormat` that models EDIFACT formats used by German utilities like, e.g.
  - `UTILMD`
  - `MSCONS`
  - `INVOIC`
  - …
- an Enum `EdifactFormatVersion` that models validity periods of different message versions, e.g.
  - `FV2310` is valid from 2023-10-01 onwards
  - `FV2404` is valid from 2024-04-03 onwards
  - …
- helper methods that allow
  - to derive the `EdifactFormat` from a given _Prüfidentifikator_ (e.g. `55001`➡`UTILMD`)
  - that derive the `EdifactFormatVersion` from a given date(time) (e.g. `2024-01-01`➡`FV2310`)

It's not much, but we need it at many places.
This is why we use this package as a central place to define these formats and versions.
There is a TypeScript clone of this package: [efoli.ts](https://github.com/Hochfrequenz/efoli.ts)

## Installation
```bash
pip install efoli
```

## Setup for Local Development
Follow the instructions from our [template repository](https://github.com/Hochfrequenz/python_template_repository?tab=readme-ov-file#how-to-use-this-repository-on-your-machine).
tl;dr: `tox`.

## Contribute
You are very welcome to contribute to this template repository by opening a pull request against the main branch.
