"""
Pytest configuration and fixtures.
"""

import pytest


@pytest.fixture
def sample_ruc() -> str:
    """Provide a sample valid RUC for testing."""
    return "20508238143"


@pytest.fixture
def sample_invalid_ruc() -> str:
    """Provide a sample invalid RUC for testing."""
    return "123456"
