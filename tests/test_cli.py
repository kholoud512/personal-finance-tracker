"""
Tests for CLI commands
Run with: poetry run pytest
"""

import pytest
from click.testing import CliRunner

from finance_tracker.cli import main
from finance_tracker.database import Category, Transaction, db


@pytest.fixture(scope="function")
def test_db():
    """Create a test database using in-memory SQLite"""
    db.init(":memory:")
    db.create_tables([Category, Transaction])

    yield db

    db.close()


@pytest.fixture
def runner():
    """Click CLI runner"""
    return CliRunner()


def test_cli_help(runner):
    result = runner.invoke(
        main,
        ["--help"],
        standalone_mode=False,
    )
    assert result.exit_code == 0
    assert "Personal Finance Tracker" in result.output


def test_cli_version(runner):
    result = runner.invoke(
        main,
        ["--version"],
        standalone_mode=False,
    )
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_add_expense(runner, test_db):
    result = runner.invoke(
        main,
        [
            "add",
            "-a",
            "50",
            "-d",
            "Lunch",
            "-c",
            "food",
            "-t",
            "expense",
        ],
        standalone_mode=False,
    )
    assert result.exit_code == 0
    assert "Added expense" in result.output
    assert Transaction.select().count() == 1


def test_add_income(runner, test_db):
    result = runner.invoke(
        main,
        [
            "add",
            "-a",
            "100",
            "-d",
            "Salary",
            "-c",
            "salary",
            "-t",
            "income",
        ],
        standalone_mode=False,
    )
    assert result.exit_code == 0
    assert "Added income" in result.output
    assert Transaction.select().count() == 1


def test_add_with_date(runner, test_db):
    date_str = "2025-11-21"
    result = runner.invoke(
        main,
        [
            "add",
            "-a",
            "75",
            "-d",
            "Dinner",
            "-c",
            "food",
            "-t",
            "expense",
            "--date",
            date_str,
        ],
        standalone_mode=False,
    )
    assert result.exit_code == 0
    assert "Added expense" in result.output
    t = Transaction.get()
    assert t.description == "Dinner"
    assert t.date.strftime("%Y-%m-%d") == date_str


def test_list_transactions(runner, test_db):
    runner.invoke(
        main,
        ["add", "-a", "50", "-d", "Lunch", "-c", "food", "-t", "expense"],
        standalone_mode=False,
    )
    runner.invoke(
        main,
        ["add", "-a", "100", "-d", "Dinner", "-c", "food", "-t", "expense"],
        standalone_mode=False,
    )

    result = runner.invoke(
        main,
        ["list-transactions"],
        standalone_mode=False,
    )
    assert result.exit_code == 0
    assert "Lunch" in result.output
    assert "Dinner" in result.output


def test_list_with_limit(runner, test_db):
    for i in range(5):
        runner.invoke(
            main,
            ["add", "-a", "10", "-d", f"Test {i}", "-c", "food", "-t", "expense"],
            standalone_mode=False,
        )

    result = runner.invoke(
        main,
        ["list-transactions", "--limit", "3"],
        standalone_mode=False,
    )
    assert result.exit_code == 0
    assert "Test 0" in result.output or "Test 4" in result.output


def test_list_filter_by_type(runner, test_db):
    runner.invoke(
        main,
        ["add", "-a", "1000", "-d", "Salary", "-c", "salary", "-t", "income"],
        standalone_mode=False,
    )
    runner.invoke(
        main,
        ["add", "-a", "50", "-d", "Food", "-c", "food", "-t", "expense"],
        standalone_mode=False,
    )

    result = runner.invoke(
        main,
        ["list-transactions", "--type", "expense"],
        standalone_mode=False,
    )
    assert result.exit_code == 0
    assert "Food" in result.output
    assert "Salary" not in result.output


def test_summary_command(runner, test_db):
    runner.invoke(
        main,
        ["add", "-a", "1000", "-d", "Salary", "-c", "salary", "-t", "income"],
        standalone_mode=False,
    )
    runner.invoke(
        main,
        ["add", "-a", "200", "-d", "Rent", "-c", "rent", "-t", "expense"],
        standalone_mode=False,
    )

    result = runner.invoke(
        main,
        ["summary"],
        standalone_mode=False,
    )
    assert result.exit_code == 0
    assert "Total Income" in result.output
    assert "Total Expenses" in result.output
    assert "Net Balance" in result.output


def test_export_command(runner, test_db, tmp_path):
    runner.invoke(
        main,
        ["add", "-a", "50", "-d", "Lunch", "-c", "food", "-t", "expense"],
        standalone_mode=False,
    )
    output_file = tmp_path / "export.csv"
    result = runner.invoke(
        main,
        ["export", "-o", str(output_file)],
        standalone_mode=False,
    )
    assert result.exit_code == 0
    assert output_file.exists()


def test_delete_command(runner, test_db):
    runner.invoke(
        main,
        ["add", "-a", "50", "-d", "Lunch", "-c", "food", "-t", "expense"],
        standalone_mode=False,
    )
    t = Transaction.get()
    result = runner.invoke(
        main,
        ["delete", str(t.id)],
        standalone_mode=False,
    )
    assert result.exit_code == 0
    assert "Deleted transaction" in result.output
    assert Transaction.select().count() == 0


def test_invalid_transaction_type(runner, test_db):
    result = runner.invoke(
        main,
        ["add", "-a", "50", "-d", "Lunch", "-c", "food", "-t", "invalid"],
    )
    assert result.exit_code != 0
    assert "not one of" in (result.output + str(result.exception or ""))


def test_missing_required_fields(runner, test_db):
    result = runner.invoke(
        main,
        ["add", "-a", "50"],
    )
    assert result.exit_code != 0
    full_output = result.output + str(result.exception or "")
    assert "Missing option" in full_output or "missing" in full_output.lower()


def test_chart_generation(runner, test_db, tmp_path):
    runner.invoke(
        main,
        ["add", "-a", "50", "-d", "Groceries", "-c", "food", "-t", "expense"],
    )
    runner.invoke(
        main,
        ["add", "-a", "30", "-d", "Bus ticket", "-c", "transport", "-t", "expense"],
    )

    output_file = tmp_path / "chart.png"
    result = runner.invoke(
        main,
        ["chart", "-o", str(output_file)],
    )

    assert result.exit_code == 0
    assert "Chart saved" in result.output
    assert output_file.exists()
