"""
Main entry point for the bank statement parser.
"""

from pathlib import Path
from core.extractor import extract_text_from_pdf
from core.text_writer import write_text_output
from factory.parser_factory import ParserFactory
from models.transaction import Transaction


def write_transactions_to_file(transactions: list[Transaction], output_path: Path):
    """
    Writes parsed transactions to a simple text file.
    """
    lines = []
    for t in transactions:
        lines.append(f"{t.date} | {t.description} | {t.amount}")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    input_dir = Path("../../input")
    raw_output_dir = Path("../../output/raw")
    output_dir = Path("../../output/parsed")

    raw_output_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in input/")
        return

    for pdf_path in pdf_files:
        print(f"\n--- Processing: {pdf_path.name} ---\n")

        # 1. Extract raw text from PDF
        raw_text = extract_text_from_pdf(pdf_path)

        raw_output_file = raw_output_dir / f"{pdf_path.stem}_raw.txt"
        raw_output_file.write_text(raw_text, encoding="utf-8")
        print(f"Saved raw text to {raw_output_file}")

        # 2. Select the correct parser using ParserFactory
        parser = ParserFactory.get_parser(raw_text)

        # 3. Parse into Transaction objects
        transactions = parser.parse(raw_text)

        # 4. Write output
        output_file = output_dir / f"{pdf_path.stem}.txt"
        write_transactions_to_file(transactions, output_file)

        print(f"Saved parsed transactions to {output_file}")


if __name__ == "__main__":
    main()
