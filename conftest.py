"""Pytest root configuration: CWD-independent basetemp isolation."""

from __future__ import annotations

from pathlib import Path
import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Bind basetemp to repository root unless explicitly provided via CLI."""
    if not getattr(config.option, "basetemp", None):
        config.option.basetemp = str(Path(config.rootpath) / ".pytest_temp")
