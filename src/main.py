'''
This is the main entry point into the program

'''
from pathlib import Path
from bank_statement_parser.core.extractor import extract_text_from_pdf
from bank_statement_parser.core.text_writer import write_text_output

def main():
    input_dir = Path("input")
    output_dir = Path("output/text")

    pdf_files= list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in input/")

    
    for pdf_path in pdf_files:
        print(f"\n--- Processing: {pdf_path.name} ---\n")
        text = extract_text_from_pdf(pdf_path)

        output_file = output_dir / f"{pdf_path.stem}.txt"

        write_text_output(text, output_file)

        print(f"Saved extracted text to {output_file}")

if __name__ == "__main__":
    main()
