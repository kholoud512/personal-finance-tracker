"""Database models and initialization
Uses Peewee ORM with SQLite
"""
import os
from datetime import datetime

from peewee import (
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    ForeignKeyField,
    Model,
    SqliteDatabase,
)

# Database file location
DB_PATH = os.path.join(os.path.expanduser("~"), ".finance_tracker.db")
db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    """Base model class"""

    class Meta:
        database = db


class Category(BaseModel):
    """Category model for grouping transactions"""

    name = CharField(unique=True, index=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "categories"

    def __str__(self):
        return self.name


class Transaction(BaseModel):
    """Transaction model for income and expenses"""

    amount = DecimalField(max_digits=10, decimal_places=2)
    description = CharField()
    category = ForeignKeyField(Category, backref="transactions")
    transaction_type = CharField(choices=[("income", "Income"), ("expense", "Expense")])
    date = DateField(default=datetime.now)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "transactions"
        indexes = ((("date", "transaction_type"), False),)

    def __str__(self):
        return f"{self.date} - {self.description}: ${self.amount}"


def init_db():
    """Initialize database and create tables safely"""
    if db.is_closed():
        db.connect()

    db.create_tables([Category, Transaction], safe=True)

    # Default categories
    default_categories = [
        "salary",
        "freelance",
        "investment",  # Income
        "food",
        "transport",
        "rent",
        "utilities",
        "entertainment",
        "shopping",
        "other",  # Expense
    ]

    for cat_name in default_categories:
        Category.get_or_create(name=cat_name)

    db.close()


def get_db():
    """Get database connection"""
    if db.is_closed():
        db.connect()
    return db


def close_db():
    """Close database connection"""
    if not db.is_closed():
        db.close()
