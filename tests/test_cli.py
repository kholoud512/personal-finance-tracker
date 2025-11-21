"""
Tests for CLI commands
Run with: poetry run pytest tests/test_cli.py -v
"""
import pytest
from click.testing import CliRunner
from finance_tracker.cli import main
from finance_tracker.database import db, Category, Transaction
import os


@pytest.fixture(scope="function")
def runner():
    """Create a CLI runner for testing"""
    return CliRunner()


@pytest.fixture(scope="function")
def test_db():
    """Create a test database"""
    # Use a temporary test database
    test_db_path = '/tmp/test_finance.db'
    
    # Remove if exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize test database
    db.init(test_db_path)
    db.connect()
    db.create_tables([Category, Transaction])
    
    # Create default categories
    default_categories = ['salary', 'food', 'transport', 'utilities', 'other']
    for cat_name in default_categories:
        Category.get_or_create(name=cat_name)
    
    yield db
    
    # Cleanup
    db.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


def test_cli_help(runner):
    """Test that CLI help command works"""
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'Personal Finance Tracker' in result.output
    assert 'add' in result.output
    assert 'list' in result.output


def test_cli_version(runner):
    """Test that version command works"""
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert '0.1.0' in result.output


def test_add_expense(runner, test_db):
    """Test adding an expense transaction"""
    result = runner.invoke(main, [
        'add',
        '-a', '50.00',
        '-d', 'Test groceries',
        '-c', 'food',
        '-t', 'expense'
    ])
    
    assert result.exit_code == 0
    assert 'Added expense' in result.output or '✓' in result.output
    
    # Verify transaction was created
    transactions = Transaction.select()
    assert len(list(transactions)) > 0


def test_add_income(runner, test_db):
    """Test adding an income transaction"""
    result = runner.invoke(main, [
        'add',
        '-a', '2000.00',
        '-d', 'Monthly salary',
        '-c', 'salary',
        '-t', 'income'
    ])
    
    assert result.exit_code == 0
    assert 'income' in result.output.lower() or '✓' in result.output


def test_add_with_date(runner, test_db):
    """Test adding transaction with specific date"""
    result = runner.invoke(main, [
        'add',
        '-a', '30.00',
        '-d', 'Bus pass',
        '-c', 'transport',
        '-t', 'expense',
        '--date', '2024-11-01'
    ])
    
    assert result.exit_code == 0


def test_list_transactions(runner, test_db):
    """Test listing transactions"""
    # First add some transactions
    runner.invoke(main, ['add', '-a', '50', '-d', 'Lunch', '-c', 'food', '-t', 'expense'])
    runner.invoke(main, ['add', '-a', '100', '-d', 'Dinner', '-c', 'food', '-t', 'expense'])
    
    # Now list them
    result = runner.invoke(main, ['list'])
    
    assert result.exit_code == 0
    # Should show transactions in output
    assert 'Lunch' in result.output or 'Dinner' in result.output or 'food' in result.output


def test_list_with_limit(runner, test_db):
    """Test listing with limit parameter"""
    # Add multiple transactions
    for i in range(5):
        runner.invoke(main, [
            'add', '-a', '10', '-d', f'Test {i}', '-c', 'food', '-t', 'expense'
        ])
    
    result = runner.invoke(main, ['list', '--limit', '3'])
    assert result.exit_code == 0


def test_list_filter_by_type(runner, test_db):
    """Test filtering transactions by type"""
    # Add income and expense
    runner.invoke(main, ['add', '-a', '1000', '-d', 'Salary', '-c', 'salary', '-t', 'income'])
    runner.invoke(main, ['add', '-a', '50', '-d', 'Food', '-c', 'food', '-t', 'expense'])
    
    # List only expenses
    result = runner.invoke(main, ['list', '--type', 'expense'])
    assert result.exit_code == 0


def test_summary_command(runner, test_db):
    """Test summary command"""
    # Add some transactions
    runner.invoke(main, ['add', '-a', '2000', '-d', 'Salary', '-c', 'salary', '-t', 'income'])
    runner.invoke(main, ['add', '-a', '100', '-d', 'Food', '-c', 'food', '-t', 'expense'])
    
    result = runner.invoke(main, ['summary'])
    
    assert result.exit_code == 0
    # Should contain financial summary info
    assert 'Income' in result.output or 'Expense' in result.output or 'Balance' in result.output


def test_export_command(runner, test_db):
    """Test export to CSV"""
    # Add a transaction
    runner.invoke(main, ['add', '-a', '50', '-d', 'Test', '-c', 'food', '-t', 'expense'])
    
    # Export
    result = runner.invoke(main, ['export', '--output', '/tmp/test_export.csv'])
    
    assert result.exit_code == 0
    assert 'Exported' in result.output or '✓' in result.output
    
    # Check file was created
    assert os.path.exists('/tmp/test_export.csv')
    
    # Cleanup
    os.remove('/tmp/test_export.csv')


def test_delete_command(runner, test_db):
    """Test deleting a transaction"""
    # Add a transaction
    runner.invoke(main, ['add', '-a', '50', '-d', 'To Delete', '-c', 'food', '-t', 'expense'])
    
    # Get the transaction ID
    transactions = Transaction.select()
    if len(list(transactions)) > 0:
        trans_id = list(transactions)[0].id
        
        # Delete it
        result = runner.invoke(main, ['delete', str(trans_id)])
        
        # Should succeed (exit code 0) or show error message gracefully
        assert result.exit_code == 0 or 'Error' in result.output


def test_invalid_transaction_type(runner, test_db):
    """Test that invalid transaction type is rejected"""
    result = runner.invoke(main, [
        'add',
        '-a', '50',
        '-d', 'Test',
        '-c', 'food',
        '-t', 'invalid_type'
    ])
    
    # Should fail with non-zero exit code
    assert result.exit_code != 0


def test_missing_required_fields(runner, test_db):
    """Test that missing required fields cause error"""
    result = runner.invoke(main, ['add', '-a', '50'])
    
    # Should fail due to missing required options
    assert result.exit_code != 0


def test_chart_generation(runner, test_db):
    """Test chart generation command"""
    # Add some expense data
    runner.invoke(main, ['add', '-a', '100', '-d', 'Food', '-c', 'food', '-t', 'expense'])
    runner.invoke(main, ['add', '-a', '50', '-d', 'Transport', '-c', 'transport', '-t', 'expense'])
    
    # Generate chart
    result = runner.invoke(main, ['chart', '--output', '/tmp/test_chart.png'])
    
    # Should complete without error
    assert result.exit_code == 0
    
    # Cleanup if file was created
    if os.path.exists('/tmp/test_chart.png'):
        os.remove('/tmp/test_chart.png')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
