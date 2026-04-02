'''
This is the main entry point into the program

'''
from pathlib import Path
from bank_statement_parser.core.extractor import extract_text_from_pdf
from bank_statement_parser.core.text_writer import write_text_output
from bank_statement_parser.core.sanitizer import sanitize_text
def main():
    input_dir = Path("input")
    output_dir = Path("output/text")

    pdf_files= list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in input/")

    
    for pdf_path in pdf_files:
        print(f"\n--- Processing: {pdf_path.name} ---\n")
        raw_text = extract_text_from_pdf(pdf_path)
        sanitized_list = sanitize_text(raw_text)
        sanitized_text = "\n".join(sanitized_list)
        output_file = output_dir / f"{pdf_path.stem}.txt"

        write_text_output(sanitized_text, output_file)

        print(f"Saved extracted text to {output_file}")

if __name__ == "__main__":
    main()
