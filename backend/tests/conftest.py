"""
Pytest configuration and fixtures.
"""
import pytest
import os


def pytest_configure(config):
    """Configure pytest."""
    # Set test environment variables if not already set
    if not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = "test-key-placeholder"
    if not os.getenv("SERPER_API_KEY"):
        os.environ["SERPER_API_KEY"] = "test-key-placeholder"


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set up test environment variables."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("SERPER_API_KEY", "test-serper-key")
    monkeypatch.setenv("ENVIRONMENT", "test")
