"""
Tests for reports and visualization module
Run with: poetry run pytest tests/test_reports.py -v
"""

from datetime import datetime

import pytest

from finance_tracker.database import Category, Transaction, db
from finance_tracker.reports import generate_chart, generate_summary, get_monthly_trend


# FIXTURES
@pytest.fixture(scope="function")
def test_db():
    """Create a fresh in-memory database for each test"""
    db.init(":memory:")
    db.create_tables([Category, Transaction])
    yield db
    db.close()


@pytest.fixture
def sample_transactions(test_db):
    """Create sample transactions for testing"""
    # Create categories
    food = Category.create(name="food")
    transport = Category.create(name="transport")
    salary = Category.create(name="salary")

    # Create transactions for November 2024
    transactions = [
        Transaction.create(
            amount=100.00,
            description="Groceries",
            category=food,
            transaction_type="expense",
            date=datetime(2024, 11, 15),
        ),
        Transaction.create(
            amount=50.00,
            description="Restaurant",
            category=food,
            transaction_type="expense",
            date=datetime(2024, 11, 20),
        ),
        Transaction.create(
            amount=30.00,
            description="Bus pass",
            category=transport,
            transaction_type="expense",
            date=datetime(2024, 11, 10),
        ),
        Transaction.create(
            amount=2000.00,
            description="Monthly salary",
            category=salary,
            transaction_type="income",
            date=datetime(2024, 11, 1),
        ),
    ]
    return transactions


# TESTS FOR generate_summary()
class TestGenerateSummary:
    """Tests for the generate_summary function"""

    def test_summary_returns_dict(self, test_db):
        """Test that summary returns a dictionary"""
        # ACT
        result = generate_summary(11, 2024)

        # ASSERT
        assert isinstance(result, dict)
        assert "total_income" in result
        assert "total_expense" in result
        assert "by_category" in result

    def test_summary_with_no_transactions(self, test_db):
        """Test summary when database is empty"""
        # ACT
        result = generate_summary(11, 2024)

        # ASSERT
        assert result["total_income"] == 0
        assert result["total_expense"] == 0
        assert result["by_category"] == []

    def test_summary_calculates_totals_correctly(self, sample_transactions):
        """Test that income and expenses are calculated correctly"""
        # ACT
        result = generate_summary(11, 2024)

        # ASSERT
        assert result["total_income"] == 2000.00  # One salary
        assert result["total_expense"] == 180.00  # 100 + 50 + 30

    def test_summary_groups_by_category(self, sample_transactions):
        """Test that expenses are grouped by category"""
        # ACT
        result = generate_summary(11, 2024)

        # ASSERT
        categories = {
            item["category"]: item["amount"] for item in result["by_category"]
        }
        assert categories["food"] == 150.00  # 100 + 50
        assert categories["transport"] == 30.00

    def test_summary_calculates_percentages(self, sample_transactions):
        """Test that category percentages are calculated"""
        # ACT
        result = generate_summary(11, 2024)

        # ASSERT
        for item in result["by_category"]:
            assert "percentage" in item
            assert 0 <= item["percentage"] <= 100

    def test_summary_filters_by_month(self, test_db):
        """Test that summary only includes transactions from specified month"""
        # ARRANGE - Create transactions in different months
        category = Category.create(name="test")
        Transaction.create(
            amount=100,
            description="Nov expense",
            category=category,
            transaction_type="expense",
            date=datetime(2024, 11, 15),
        )
        Transaction.create(
            amount=200,
            description="Oct expense",
            category=category,
            transaction_type="expense",
            date=datetime(2024, 10, 15),
        )

        # ACT
        nov_result = generate_summary(11, 2024)
        oct_result = generate_summary(10, 2024)

        # ASSERT
        assert nov_result["total_expense"] == 100
        assert oct_result["total_expense"] == 200


# TESTS FOR generate_chart()
class TestGenerateChart:
    """Tests for the generate_chart function"""

    def test_chart_creates_file(self, sample_transactions, tmp_path):
        """Test that chart function creates an image file"""
        # ARRANGE
        output_file = tmp_path / "test_chart.png"

        # ACT
        generate_chart(11, 2024, str(output_file))

        # ASSERT
        assert output_file.exists()
        assert output_file.stat().st_size > 0  # File is not empty

    def test_chart_handles_no_data(self, test_db, tmp_path, capsys):
        """Test that chart handles empty data gracefully"""
        # ARRANGE
        output_file = tmp_path / "empty_chart.png"

        # ACT
        generate_chart(11, 2024, str(output_file))

        # ASSERT
        captured = capsys.readouterr()
        assert "No expense data" in captured.out
        assert not output_file.exists()  # No file created

    def test_chart_with_custom_filename(self, sample_transactions, tmp_path):
        """Test that chart respects custom output filename"""
        # ARRANGE
        custom_name = tmp_path / "my_custom_chart.png"

        # ACT
        generate_chart(11, 2024, str(custom_name))

        # ASSERT
        assert custom_name.exists()


# TESTS FOR get_monthly_trend()
class TestGetMonthlyTrend:
    """Tests for the get_monthly_trend function"""

    def test_trend_returns_all_months(self, test_db):
        """Test that trend returns data for all 12 months"""
        # ACT
        result = get_monthly_trend(2024)

        # ASSERT
        assert len(result) == 12
        assert all(month in result for month in range(1, 13))

    def test_trend_structure(self, test_db):
        """Test that each month has income and expense keys"""
        # ACT
        result = get_monthly_trend(2024)

        # ASSERT
        for month_data in result.values():
            assert "income" in month_data
            assert "expense" in month_data

    def test_trend_calculates_correctly(self, sample_transactions):
        """Test that monthly trend calculates correctly"""
        # ACT
        result = get_monthly_trend(2024)

        # ASSERT - November should have our sample data
        assert result[11]["income"] == 2000.00
        assert result[11]["expense"] == 180.00

        # Other months should be zero
        assert result[10]["income"] == 0
        assert result[10]["expense"] == 0
