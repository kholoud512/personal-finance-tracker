"""Personal Finance Tracker CLI - Main command-line interface module"""

import sys
from datetime import datetime

import click
from rich import box
from rich.console import Console
from rich.table import Table

from finance_tracker.logger import logger

from .database import Category, Transaction, init_db
from .reports import generate_chart, generate_summary

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Personal Finance Tracker - Manage your income and expenses"""
    logger.debug("CLI application started")

    # Prevent DB initialization during tests
    if not getattr(sys, "_called_from_test", False):
        init_db()


# ADD TRANSACTION
@main.command()
@click.option("--amount", "-a", type=float, required=True, help="Transaction amount")
@click.option("--description", "-d", required=True, help="Transaction description")
@click.option("--category", "-c", required=True, help="Category")
@click.option(
    "--type",
    "-t",
    "trans_type",
    type=click.Choice(["income", "expense"]),
    required=True,
    help="Transaction type",
)
@click.option(
    "--date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=lambda: datetime.now().strftime("%Y-%m-%d"),
    show_default=True,
    help="Transaction date (YYYY-MM-DD)",
)
def add(amount, description, category, trans_type, date):
    """
    Add a new transaction
    This function creates a new transaction record with the specified details,
    including amount, description, category, and type (income or expense).

    Args:
        amount (float): The transaction amount in currency units
        description (str): A brief description of the transaction
        category (str): The category name (e.g., 'food', 'salary', 'transport')
        transaction_type (str): Either 'income' or 'expense'
        date (str): Transaction date in YYYY-MM-DD format

    Returns:
        None

    Example:
        >>> add(50.0, "Groceries", "food", "expense", "2024-11-27")
    """
    logger.info(
        f"CLI: Adding {trans_type} - Amount: ${amount}, "
        f"Category: {category}, Description: {description}"
    )

    try:
        cat, _ = Category.get_or_create(name=category.lower())
        Transaction.create(
            amount=amount,
            description=description,
            category=cat,
            transaction_type=trans_type,
            date=date,
        )

        console.print(
            f"[green]✓[/green] Added {trans_type}: {description} - ${amount:.2f}",
            style="bold",
        )

        logger.debug("Transaction added successfully via CLI")

    except Exception as e:
        logger.error(f"CLI add command failed: {e}")

        if getattr(sys, "_called_from_test", False):
            raise e
        console.print(f"[red]Error:[/red] {str(e)}")


# LIST TRANSACTIONS
@main.command()
@click.option("--limit", "-l", default=10, help="Number of transactions to show")
@click.option(
    "--type",
    "-t",
    "trans_type",
    type=click.Choice(["income", "expense", "all"]),
    default="all",
    show_default=True,
    help="Filter by transaction type",
)
def list_transactions(limit, trans_type):
    """List recent transactions"""
    try:
        query = Transaction.select().order_by(Transaction.date.desc()).limit(limit)

        if trans_type != "all":
            query = query.where(Transaction.transaction_type == trans_type)

        transactions = list(query)

        if not transactions:
            console.print("[yellow]No transactions found[/yellow]")
            return

        table = Table(
            title=f"Recent Transactions ({trans_type})",
            box=box.ROUNDED,
        )

        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Date", style="magenta")
        table.add_column("Description", style="white")
        table.add_column("Category", style="blue")
        table.add_column("Type", style="yellow")
        table.add_column("Amount", justify="right", style="green")

        for trans in transactions:
            color = "green" if trans.transaction_type == "income" else "red"
            amount_str = f"[{color}]${trans.amount:.2f}[/{color}]"

            table.add_row(
                str(trans.id),
                trans.date.strftime("%Y-%m-%d"),
                trans.description,
                trans.category.name,
                trans.transaction_type,
                amount_str,
            )

        console.print(table)

    except Exception as e:
        if getattr(sys, "_called_from_test", False):
            raise e
        console.print(f"[red]Error:[/red] {str(e)}")


# SUMMARY
@main.command()
@click.option("--month", "-m", type=int, help="Month (1–12)")
@click.option("--year", "-y", type=int, help="Year (YYYY)")
def summary(month, year):
    """Show financial summary"""
    try:
        now = datetime.now()
        month = month or now.month
        year = year or now.year

        summary_data = generate_summary(month, year)

        console.print(f"\n[bold cyan]Financial Summary - {month}/{year}[/bold cyan]\n")

        console.print(
            f"[green]Total Income:[/green]  ${summary_data['total_income']:.2f}"
        )
        console.print(
            f"[red]Total Expenses:[/red] ${summary_data['total_expense']:.2f}"
        )

        balance = summary_data["total_income"] - summary_data["total_expense"]
        color = "green" if balance >= 0 else "red"

        console.print(f"[{color}]Net Balance:[/{color}]   ${balance:.2f}\n")

        if summary_data["by_category"]:
            table = Table(title="Expenses by Category", box=box.SIMPLE)
            table.add_column("Category", style="cyan")
            table.add_column("Amount", justify="right", style="red")
            table.add_column("Percentage", justify="right", style="yellow")

            for item in summary_data["by_category"]:
                table.add_row(
                    item["category"],
                    f"${item['amount']:.2f}",
                    f"{item['percentage']:.1f}%",
                )

            console.print(table)

    except Exception as e:
        if getattr(sys, "_called_from_test", False):
            raise e
        console.print(f"[red]Error:[/red] {str(e)}")


# CHART GENERATION
@main.command()
@click.option("--month", "-m", type=int, help="Month (1–12)")
@click.option("--year", "-y", type=int, help="Year (YYYY)")
@click.option(
    "--output", "-o", default="chart.png", show_default=True, help="Output file"
)
def chart(month, year, output):
    """Generate expense chart"""
    try:
        now = datetime.now()
        month = month or now.month
        year = year or now.year

        # Generate file so tests pass
        generate_chart(month, year, output)

        console.print(f"[green]✓[/green] Chart saved to: {output}")

    except Exception as e:
        if getattr(sys, "_called_from_test", False):
            raise e
        console.print(f"[red]Error:[/red] {str(e)}")


# DELETE TRANSACTION
@main.command()
@click.argument("transaction_id", type=int)
def delete(transaction_id):
    """Delete a transaction by ID"""
    logger.warning(f"CLI: User requesting deletion of transaction {transaction_id}")
    try:
        transaction = Transaction.get_by_id(transaction_id)
        desc = transaction.description
        transaction.delete_instance()

        console.print(f"[green]✓[/green] Deleted transaction: {desc}")

    except Transaction.DoesNotExist:
        console.print(f"[red]Error:[/red] Transaction {transaction_id} not found")

    except Exception as e:
        if getattr(sys, "_called_from_test", False):
            raise e
        console.print(f"[red]Error:[/red] {str(e)}")


# EXPORT CSV
@main.command()
@click.option(
    "--output", "-o", default="export.csv", show_default=True, help="CSV file"
)
def export(output):
    """Export all transactions to CSV"""
    logger.info(f"CLI: Exporting transactions to {output}")
    try:
        import pandas as pd

        transactions = Transaction.select()

        data = [
            {
                "id": t.id,
                "date": t.date,
                "description": t.description,
                "category": t.category.name,
                "type": t.transaction_type,
                "amount": t.amount,
            }
            for t in transactions
        ]

        pd.DataFrame(data).to_csv(output, index=False)

        console.print(
            f"[green]✓[/green] Exported {len(data)} transactions to: {output}"
        )

        logger.info(f"CLI: Successfully exported {len(data)} transactions")

    except Exception as e:
        if getattr(sys, "_called_from_test", False):
            raise e
        console.print(f"[red]Error:[/red] {str(e)}")


if __name__ == "__main__":
    main()
