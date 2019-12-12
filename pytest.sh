#!/bin/bash

set -e

cd "$(dirname "$0")" || exit 1
PYTHONPATH=src python3 -m pytest

python3 -m flake8

codespell -S "*.pyc,.*.swp" *
