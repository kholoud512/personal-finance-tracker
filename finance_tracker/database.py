"""Database models and initialization
Uses Peewee ORM with SQLite
Operations with logging suppor
"""
from datetime import datetime
from pathlib import Path

from peewee import (
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    ForeignKeyField,
    Model,
    SqliteDatabase,
)

# Import the logger
from finance_tracker.logger import logger

# Database path
DB_PATH = Path.home() / ".finance_tracker.db"
db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class Category(BaseModel):
    name = CharField(unique=True, index=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "categories"

    def __str__(self):
        return self.name


class Transaction(BaseModel):
    """
    Database model for storing financial transactions.

    Attributes:
        amount (DecimalField): Transaction amount
        description (TextField): Transaction description
        category (ForeignKeyField): Reference to transaction category
        transaction_type (CharField): Type of transaction ('income' or 'expense')
        date (DateField): Date of the transaction
        created_at (DateTimeField): Timestamp when record was created
    """

    amount = DecimalField(decimal_places=2)
    description = CharField()
    category = ForeignKeyField(Category, backref="transactions")
    transaction_type = CharField()
    date = DateField(default=datetime.now)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "transactions"
        indexes = ((("date", "transaction_type"), False),)

    def __str__(self):
        return f"{self.date} - {self.description}: ${self.amount}"


def init_db():
    """Initialize database connection and create tables safely"""
    logger.info(f"Initializing database at: {DB_PATH}")

    try:
        db.init(str(DB_PATH))
        db.connect(reuse_if_open=True)
        db.create_tables([Category, Transaction], safe=True)
        logger.debug("Database tables created successfully")

        # Default categories
        default_categories = [
            "salary",
            "freelance",
            "investment",
            "food",
            "transport",
            "rent",
            "utilities",
            "entertainment",
            "shopping",
            "other",
        ]
        for cat_name in default_categories:
            Category.get_or_create(name=cat_name.lower())

    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        raise
    finally:
        if not db.is_closed():
            db.close()


def add_transaction(amount, description, category_name, trans_type, date=None):
    """Add a new transaction to the database with logging"""
    logger.info(f"Adding {trans_type}: {amount} - '{description}' [{category_name}]")
    try:
        category, created = Category.get_or_create(name=category_name.lower())
        if created:
            logger.debug(f"Created new category: '{category_name}'")

        transaction = Transaction.create(
            amount=amount,
            description=description,
            category=category,
            transaction_type=trans_type,
            date=date or datetime.now(),
        )
        logger.debug(f"Transaction saved with ID: {transaction.id}")
        return transaction
    except Exception as e:
        logger.error(f"Failed to add transaction: {e}", exc_info=True)
        raise


def delete_transaction(transaction_id):
    """Delete a transaction by ID with logging"""
    logger.warning(f"Deleting transaction ID: {transaction_id}")
    try:
        transaction = Transaction.get_by_id(transaction_id)
        desc = transaction.description
        transaction.delete_instance()
        logger.info(f"Deleted transaction: '{desc}' (ID: {transaction_id})")
        return True
    except Transaction.DoesNotExist:
        logger.error(f"Transaction not found: ID {transaction_id}")
        raise


def get_db():
    """Get database connection"""
    if db.is_closed():
        db.connect()
    return db


def close_db():
    """Close database connection"""
    if not db.is_closed():
        db.close()
