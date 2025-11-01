"""Pytest configuration and shared fixtures"""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """Path to project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def examples_dir(project_root):
    """Path to examples directory"""
    return project_root / "examples"


@pytest.fixture(scope="session")
def schemas_dir(project_root):
    """Path to schemas directory"""
    return project_root / "schemas"


@pytest.fixture(scope="session")
def domain_stories_example(examples_dir):
    """Path to domain stories example file"""
    return examples_dir / "cb-domain-stories.yaml"


@pytest.fixture(scope="session")
def strategic_example(examples_dir):
    """Path to strategic DDD example file"""
    return examples_dir / "payments-strategic.yaml"


@pytest.fixture(scope="session")
def tactical_example(examples_dir):
    """Path to tactical DDD example file"""
    return examples_dir / "payments-tactical.yaml"
