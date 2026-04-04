import csv
from pathlib import Path
from models.transaction import Transaction


def write_transactions_to_csv(transactions: list[Transaction], output_path: Path):
    """
    Writes parsed transactions to a CSV file with columns:
    Date, Amount, Description

    All fields are safely quoted to avoid CSV parsing issues.
    """

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header row
        writer.writerow(["Date", "Amount", "Description"])

        for t in transactions:
            date_str = t.date.isoformat()
            amount_str = f"{t.amount:.2f}"
            desc_str = t.description.replace("\n", " ").strip()

            writer.writerow([date_str, amount_str, desc_str])