"""Personal Finance Tracker CLI
Main command-line interface module
"""
from datetime import datetime

import click
from rich import box
from rich.console import Console
from rich.table import Table

from .database import Category, Transaction, init_db
from .reports import generate_chart, generate_summary

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Personal Finance Tracker - Manage your income and expenses"""
    import sys

    if not getattr(sys, "_called_from_test", False):
        init_db()


@main.command()
@click.option(
    "--amount",
    "-a",
    type=float,
    required=True,
    help="Transaction amount",
)
@click.option(
    "--description",
    "-d",
    required=True,
    help="Transaction description",
)
@click.option(
    "--category",
    "-c",
    required=True,
    help="Category (e.g., food, transport, salary)",
)
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
    default=str(datetime.now().date()),
    help="Transaction date (YYYY-MM-DD)",
)
def add(amount, description, category, trans_type, date):
    """Add a new transaction"""
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
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@main.command()
@click.option(
    "--limit",
    "-l",
    default=10,
    help="Number of transactions to show",
)
@click.option(
    "--type",
    "-t",
    "trans_type",
    type=click.Choice(["income", "expense", "all"]),
    default="all",
    help="Filter by transaction type",
)
def list_transactions(limit, trans_type):
    """List recent transactions"""
    try:
        query = Transaction.select().order_by(Transaction.date.desc()).limit(limit)

        if trans_type != "all":
            query = query.where(Transaction.transaction_type == trans_type)

        transactions = [t for t in query]

        if not transactions:
            console.print("[yellow]No transactions found[/yellow]")
            return

        table = Table(
            title=f"Recent Transactions ({trans_type})",
            box=box.ROUNDED
        )
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Date", style="magenta")
        table.add_column("Description", style="white")
        table.add_column("Category", style="blue")
        table.add_column("Type", style="yellow")
        table.add_column("Amount", justify="right", style="green")

        for trans in transactions:
            amount_str = f"${trans.amount:.2f}"
            color = "green" if trans.transaction_type == "income" else "red"
            table.add_row(
                str(trans.id),
                trans.date.strftime("%Y-%m-%d"),
                trans.description,
                trans.category.name,
                trans.transaction_type,
                f"[{color}]{amount_str}[/{color}]",
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@main.command()
@click.option(
    "--month",
    "-m",
    type=int,
    help="Month (1-12)",
)
@click.option(
    "--year",
    "-y",
    type=int,
    help="Year",
)
def summary(month, year):
    """Show financial summary"""
    try:
        current_date = datetime.now()
        month = month or current_date.month
        year = year or current_date.year

        summary_data = generate_summary(month, year)

        console.print(
            f"\n[bold cyan]Financial Summary - {month}/{year}[/bold cyan]\n"
        )
        console.print(
            f"[green]Total Income:[/green]  ${summary_data['total_income']:.2f}"
        )
        console.print(
            f"[red]Total Expenses:[/red] ${summary_data['total_expense']:.2f}"
        )

        balance = summary_data["total_income"] - summary_data["total_expense"]
        balance_color = "green" if balance >= 0 else "red"
        console.print(
    f"[{balance_color}]Net Balance:[/{balance_color}]   ${balance:.2f}\n"
    )

        if summary_data["by_category"]:
            table = Table(title="Expenses by Category", box=box.SIMPLE)
            table.add_column("Category", style="cyan")
            table.add_column("Amount", justify="right", style="red")
            table.add_column("Percentage", justify="right", style="yellow")

            for cat_data in summary_data["by_category"]:
                table.add_row(
                    cat_data["category"],
                    f"${cat_data['amount']:.2f}",
                    f"{cat_data['percentage']:.1f}%",
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@main.command()
@click.option(
    "--month",
    "-m",
    type=int,
    help="Month (1-12)",
)
@click.option(
    "--year",
    "-y",
    type=int,
    help="Year",
)
@click.option(
    "--output",
    "-o",
    default="chart.png",
    help="Output filename",
)
def chart(month, year, output):
    """Generate expense chart"""
    try:
        current_date = datetime.now()
        month = month or current_date.month
        year = year or current_date.year

        generate_chart(month, year, output)
        console.print(f"[green]✓[/green] Chart saved to: {output}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@main.command()
@click.argument("transaction_id", type=int)
def delete(transaction_id):
    """Delete a transaction by ID"""
    try:
        transaction = Transaction.get_by_id(transaction_id)
        description = transaction.description
        transaction.delete_instance()
        console.print(f"[green]✓[/green] Deleted transaction: {description}")

    except Transaction.DoesNotExist:
        console.print(f"[red]Error:[/red] Transaction {transaction_id} not found")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@main.command()
@click.option(
    "--output",
    "-o",
    default="export.csv",
    help="Output CSV file",
)
def export(output):
    """Export all transactions to CSV"""
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

        df = pd.DataFrame(data)
        df.to_csv(output, index=False)

        console.print(
            f"[green]✓[/green] Exported {len(data)} transactions to: {output}"
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


if __name__ == "__main__":
    main()
