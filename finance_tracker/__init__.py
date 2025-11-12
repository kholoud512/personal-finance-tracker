"""
Personal Finance Tracker
A CLI application for managing personal finances
"""

__version__ = "0.1.0"
__author__ = "Kholoud Ibrahim"
__email__ = "thmanabrahym512@gmail.com"

from .database import init_db, Transaction, Category
from .cli import main

__all__ = ['init_db', 'Transaction', 'Category', 'main']
