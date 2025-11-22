"""
Reports and data visualization module
"""
import matplotlib.pyplot as plt
from peewee import fn

from finance_tracker.logger import logger

from .database import Transaction


def generate_summary(month, year):
    """
    Generate financial summary for a given month/year

    Args:
        month: Month number (1-12)
        year: Year (e.g., 2024)

    Returns:
        Dictionary with summary data
    """
    logger.info(f"Generating summary for {month}/{year}")

    # Query transactions for the specified month using SQLite strftime
    transactions = Transaction.select().where(
        (fn.strftime("%m", Transaction.date) == f"{month:02d}")
        & (fn.strftime("%Y", Transaction.date) == str(year))
    )

    total_income = 0
    total_expense = 0
    expenses_by_category = {}

    for trans in transactions:
        if trans.transaction_type == "income":
            total_income += float(trans.amount)
        else:
            total_expense += float(trans.amount)
            cat_name = trans.category.name
            expenses_by_category[cat_name] = expenses_by_category.get(
                cat_name, 0
            ) + float(trans.amount)

    # Calculate percentages
    category_data = []
    for cat, amount in sorted(
        expenses_by_category.items(), key=lambda x: x[1], reverse=True
    ):
        percentage = (amount / total_expense * 100) if total_expense > 0 else 0
        category_data.append(
            {"category": cat, "amount": amount, "percentage": percentage}
        )

        logger.debug(
            f"Summary complete - Income: ${total_income}, "
            f"Expenses: ${total_expense}"
        )

    if not expenses_by_category:
        logger.warning(f"No expenses found for {month}/{year}")

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "by_category": category_data,
    }


def generate_chart(month, year, output_file="chart.png"):
    """
    Generate pie chart of expenses by category

    Args:
        month: Month number (1-12)
        year: Year (e.g., 2024)
        output_file: Output filename for the chart
    """
    logger.info(f"Generating expense chart for {month}/{year}")
    summary = generate_summary(month, year)

    if not summary["by_category"]:
        logger.warning(f"No expense data to visualize for {month}/{year}")
        print("No expense data to visualize")
        return

    # Prepare data for pie chart
    categories = [item["category"] for item in summary["by_category"]]
    amounts = [item["amount"] for item in summary["by_category"]]

    # Create pie chart
    plt.figure(figsize=(10, 8))
    colors = plt.cm.Set3.colors
    explode = [0.05 if i == 0 else 0 for i in range(len(categories))]

    plt.pie(
        amounts,
        labels=categories,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        explode=explode,
        shadow=True,
    )

    plt.title(f"Expenses by Category - {month}/{year}", fontsize=16, fontweight="bold")
    plt.axis("equal")

    # Add summary text
    total_expense = summary["total_expense"]
    plt.text(
        0,
        -1.3,
        f"Total Expenses: ${total_expense:.2f}",
        ha="center",
        fontsize=12,
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    plt.tight_layout()
    try:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        logger.info(f"Chart saved successfully: {output_file}")
    except Exception as e:
        logger.error(f"Failed to save chart: {e}", exc_info=True)
        raise
    finally:
        plt.close()


def get_monthly_trend(year):
    """
    Get income and expense trends for each month of the year

    Args:
        year: Year to analyze

    Returns:
        Dictionary with monthly data
    """
    monthly_data = {month: {"income": 0, "expense": 0} for month in range(1, 13)}

    transactions = Transaction.select().where(
        fn.strftime("%Y", Transaction.date) == str(year)
    )

    for trans in transactions:
        month = trans.date.month
        if trans.transaction_type == "income":
            monthly_data[month]["income"] += float(trans.amount)
        else:
            monthly_data[month]["expense"] += float(trans.amount)

    return monthly_data
