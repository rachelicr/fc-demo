# conftest.py
import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "local_only: requires local credentials (skipped in CI)"
    )