import sys

import pytest

from finance_tracker.database import db, init_db

sys._called_from_test = True


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initialize in-memory database for testing"""
    db.init(":memory:")
    init_db()
    yield
    db.close()
