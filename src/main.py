"""
Main entry point for the bank statement parser.
"""

from pathlib import Path
from core.extractor import extract_text_from_pdf
from core.text_writer import write_transactions_to_file
from core.csv_writer import write_transactions_to_csv
from core.owner_detector import extract_owner_name
from factory.parser_detector import detect_parser, detect_account_type, detect_bank
from models.transaction import Transaction

def main():
    BASE_DIR       = Path(__file__).resolve().parent.parent
    input_dir      = BASE_DIR / "input"
    raw_output_dir = BASE_DIR / "output" / "raw"
    output_txt     = BASE_DIR / "output" / "text"
    output_csv     = BASE_DIR / "output" / "csv"


    raw_output_dir.mkdir(parents=True, exist_ok=True)
    output_txt.mkdir(parents=True, exist_ok=True)
    output_csv.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in input/")
        return

    for pdf_path in pdf_files:
        print(f"\n--- Processing: {pdf_path.name} ---\n")

        # Extract raw text from PDF
        raw_text = extract_text_from_pdf(pdf_path)

        raw_output_file = raw_output_dir / f"{pdf_path.stem}_raw.txt"
        raw_output_file.write_text(raw_text, encoding="utf-8")
        print(f"Saved raw text to {raw_output_file}")

        # Select the bank 
        bank = detect_bank(raw_text)
        parser = detect_parser(raw_text)

        # Parse into Transaction objects
        transactions = parser.parse(raw_text)

        # Detect Owner
        owner = extract_owner_name(raw_text, bank)

        # 4. Write output
        output_txt_file = output_txt / f"{owner}_{pdf_path.stem}.txt"
        output_csv_file = output_csv / f"{owner}_{pdf_path.stem}.txt"
        write_transactions_to_file(transactions, output_txt_file)
        write_transactions_to_csv(transactions, output_csv_file)
        print(f"Saved parsed transactions to {output_csv_file} and {output_txt_file}")


if __name__ == "__main__":
    main()
