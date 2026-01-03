"""
Tests for database models
Run with: poetry run pytest
"""

from datetime import datetime

import pytest
from peewee import IntegrityError

from finance_tracker.database import Category, Transaction, db


# FIXTURE — fresh in-memory DB before each test
@pytest.fixture(scope="function")
def test_db():
    """Create a test database"""
    # Use in memory database for tests
    db.init(":memory:")
    db.create_tables([Category, Transaction])

    yield db

    db.close()


# TEST 1 — Category creation
def test_category_creation(test_db):
    """Test creating a category"""
    category = Category.create(name="test_category")

    assert category.id is not None
    assert category.name == "test_category"
    assert isinstance(category.created_at, datetime)


# TEST 2 — Unique category constraint
def test_category_unique_constraint(test_db):
    """Test that category names are unique"""
    Category.create(name="food")

    # Use correct exception (not generic Exception)
    with pytest.raises(IntegrityError):
        Category.create(name="food")


# TEST 3 — Transaction creation
def test_transaction_creation(test_db):
    """Test creating a transaction"""
    category = Category.create(name="salary")

    transaction = Transaction.create(
        amount=1000.00,
        description="Monthly salary",
        category=category,
        transaction_type="income",
        date=datetime.now(),
    )

    assert transaction.id is not None
    assert float(transaction.amount) == 1000.00
    assert transaction.description == "Monthly salary"
    assert transaction.category.name == "salary"
    assert transaction.transaction_type == "income"


# TEST 4 — Income vs Expense types
def test_transaction_types(test_db):
    """Test income and expense transactions"""
    cat_income = Category.create(name="salary")
    cat_expense = Category.create(name="food")

    income = Transaction.create(
        amount=2000,
        description="Salary",
        category=cat_income,
        transaction_type="income",
    )

    expense = Transaction.create(
        amount=50,
        description="Groceries",
        category=cat_expense,
        transaction_type="expense",
    )

    assert income.transaction_type == "income"
    assert expense.transaction_type == "expense"


# TEST 5 — Category: Transactions relationship
def test_transaction_category_relationship(test_db):
    """Test relationship between Transactions and Categories"""
    category = Category.create(name="transport")

    Transaction.create(
        amount=20,
        description="Bus ticket",
        category=category,
        transaction_type="expense",
    )

    Transaction.create(
        amount=15,
        description="Metro card",
        category=category,
        transaction_type="expense",
    )

    # Category should have 2 transactions
    assert len(list(category.transactions)) == 2


# TEST 6 — Querying transactions
def test_transaction_query(test_db):
    """Test querying transactions"""
    cat = Category.create(name="food")

    Transaction.create(
        amount=30,
        description="Lunch",
        category=cat,
        transaction_type="expense",
    )
    Transaction.create(
        amount=50,
        description="Dinner",
        category=cat,
        transaction_type="expense",
    )

    # Query all expensses
    expenses = Transaction.select().where(Transaction.transaction_type == "expense")

    assert len(list(expenses)) == 2


# MAIN — run manually if needed
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
