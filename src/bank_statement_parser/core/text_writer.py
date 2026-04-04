from pathlib import Path
from models.transaction import Transaction

def write_transactions_to_file(transactions: list[Transaction], output_path: Path):
    """
    Writes parsed transactions to a left-aligned, column-aligned table.
    Columns: Date | Amount | Description
    """

    # Convert transactions into raw string fields
    rows = []
    for t in transactions:
        date_str = t.date.isoformat()
        amount_str = f"{t.amount:.2f}"
        desc_str = t.description.replace("\n", " ").strip()
        rows.append((date_str, amount_str, desc_str))

    # Compute max width for each column
    max_date = max(len(r[0]) for r in rows)
    max_amount = max(len(r[1]) for r in rows)
    max_desc = max(len(r[2]) for r in rows)

    # Header row
    header = (
        f"{'Date'.ljust(max_date)}\t"
        f"{'Amount'.ljust(max_amount)}\t"
        f"{'Description'.ljust(max_desc)}"
    )

    lines = [header]

    # Data rows
    for date_str, amount_str, desc_str in rows:
        line = (
            f"{date_str.ljust(max_date)}\t"
            f"{amount_str.ljust(max_amount)}\t"
            f"{desc_str.ljust(max_desc)}"
        )
        lines.append(line)

    output_path.write_text("\n".join(lines), encoding="utf-8")
