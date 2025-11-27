# Getting Started with Personal Finance Tracker

## Introduction

This tutorial will walk you through installing and using the Personal Finance Tracker CLI application. You'll learn how to track your income, expenses, and generate financial reports.

## Prerequisites

- Python 3.9 or higher installed
- Poetry installed on your system
- Basic command-line knowledge

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/kholoud512/personal-finance-tracker.git
cd personal-finance-tracker
```

### Step 2: Install Dependencies
```bash
poetry install
```

This will:
- Create a virtual environment
- Install all required packages
- Set up the `finance` CLI command

### Step 3: Activate Poetry Shell
```bash
poetry shell
```

Now you're ready to use the finance tracker!

## Basic Usage Tutorial

### Adding Your First Expense

Let's track a grocery shopping trip:
```bash
finance add -a 45.50 -d "Weekly groceries at Carrefour" -c food -t expense
```

**Explanation:**
- `-a 45.50` → Amount: €45.50
- `-d "..."` → Description of the transaction
- `-c food` → Category: food
- `-t expense` → Type: expense

You should see:  Transaction added successfully!

### Adding Income

Track your monthly salary:
```bash
finance add -a 2500.00 -d "November salary" -c salary -t income
```

### Adding More Transactions

Let's add a few more to build up your data:
```bash
# Transportation
finance add -a 15.00 -d "Bus pass" -c transport -t expense

# Entertainment
finance add -a 30.00 -d "Cinema tickets" -c entertainment -t expense

# Utilities
finance add -a 80.00 -d "Electricity bill" -c utilities -t expense
```

### Viewing Your Transactions

List all transactions:
```bash
finance list
```

This shows a formatted table with:
- Transaction ID
- Date
- Description
- Category
- Amount
- Type (Income/Expense)

To see more transactions:
```bash
finance list --limit 20
```

To filter by type:
```bash
finance list --type income
finance list --type expense
```

### Generating a Monthly Summary

See your financial overview:
```bash
finance summary
```

This displays:
- 💰 Total Income
- 💸 Total Expenses
- 💵 Net Savings

For a specific month:
```bash
finance summary --month 10 --year 2024
```

### Creating Visual Reports

Generate a pie chart of your expenses:
```bash
finance chart
```

This creates `expense_breakdown.png` in your current directory.

For a specific month:
```bash
finance chart --month 11 --year 2024 --output november_expenses.png
```

### Exporting Data

Export all transactions to CSV for use in Excel:
```bash
finance export
```

This creates `transactions.csv` in the current directory.

Custom filename:
```bash
finance export --output my_finances_2024.csv
```

### Deleting a Transaction

First, list your transactions to find the ID:
```bash
finance list
```

Then delete by ID:
```bash
finance delete 5
```

Replace `5` with the actual transaction ID.

## Real-World Example Workflow

Let's track a full week:
```bash
# Monday - Salary day!
finance add -a 2500.00 -d "Monthly salary" -c salary -t income

# Tuesday - Expenses
finance add -a 12.50 -d "Lunch" -c food -t expense
finance add -a 5.00 -d "Coffee" -c food -t expense

# Wednesday - Shopping
finance add -a 65.00 -d "Groceries" -c food -t expense
finance add -a 40.00 -d "New shirt" -c clothing -t expense

# Thursday - Bills
finance add -a 100.00 -d "Internet" -c utilities -t expense

# Friday - Entertainment
finance add -a 25.00 -d "Restaurant dinner" -c food -t expense

# Weekend review
finance summary
finance chart
```

## Tips and Best Practices

1. **Be consistent with categories**: Use the same category names (food, transport, utilities)
2. **Add descriptions**: Clear descriptions help you remember transactions later
3. **Regular reviews**: Run `finance summary` weekly to track your spending
4. **Use date flags**: Add `--date YYYY-MM-DD` for backdated transactions
5. **Export monthly**: Keep CSV backups at the end of each month

## Troubleshooting

### Command not found

**Problem:** `finance: command not found`

**Solution:** Make sure you're in the poetry shell:
```bash
poetry shell
```

### Database errors

**Problem:** SQLite database errors

**Solution:** Reset the database:
```bash
# Linux/Mac
rm ~/.finance_tracker.db

# Windows
del %USERPROFILE%\.finance_tracker.db

# Then recreate by running any command
finance list
```

### Poetry not found

**Problem:** `poetry: command not found`

**Solution:** Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## Next Steps

Now that you're comfortable with the basics:

- Set monthly budgets for each category
- Track your spending patterns over time
- Use the CSV export to create custom reports
- Share expense reports with family members

## Need Help?

- Check the main README: [README.md](../../README.md)
- View API documentation: Run `poetry run pdoc --html finance_tracker -o docs/api`
- Report issues: [GitHub Issues](https://github.com/kholoud512/personal-finance-tracker/issues)

Happy tracking!
