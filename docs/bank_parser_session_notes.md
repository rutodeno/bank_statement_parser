# BANK STATEMENT PARSER — MASTER ROADMAP

This document outlines the development plan for a multi‑bank, multi‑format
statement ingestion engine supporting NFCU and AMEX (checking + credit).

---

# GOALS

1. Process bank statements for:
   • Navy Federal (NFCU) — debit/checking + credit card  
   • American Express (AMEX) — checking + credit card

   Supported input formats:
   • PDF → extract text  
   • TXT → read directly  
   • CSV → parse rows into transactions

2. Detect:
   • Bank (NFCU vs AMEX)  
   • Account type (checking vs credit card)  
   • Account owner name (bank‑specific header extraction)

3. Aggregate transactions by month:
   • Group by (year, month)  
   • If a month file exists → append  
   • If not → create a new file  
   • If a statement spans multiple months → split transactions into correct buckets

4. Process both debit and credit transactions within the same statement:
   • Extract debit transactions  
   • Extract credit transactions  
   • Return a unified ParsedStatement object  
   • Enable analytics: - total money in  
    - total money out  
    - net flow  
    - spending categories

5. Save output files using naming convention:
   `{owner}_{bank}_{accounttype}_{month}_{year}.txt`

---

# ARCHITECTURE PLAN

### • Input Handler

- Detect file type (pdf/txt/csv)
- PDF → `extract_text_from_pdf()`
- TXT → read file
- CSV → parse into rows
- Return raw text for parser detection

### • parser_detector.py

- High‑confidence bank detection (header + signal scoring)
- Bank‑specific account type detection
- Routing table → returns correct parser instance

### • Owner Name Extraction

- `extract_owner_name(text, bank)`
- AMEX:
  - header block
  - name lines
  - “Account Ending In …”
- NFCU:
  - “Member:”
  - “Primary Owner:”

### • ParsedStatement model

- `owner: str`
- `bank: Bank`
- `account_type: AccountType`
- `debits: list[Transaction]`
- `credits: list[Transaction]`
- `period_start: date`
- `period_end: date`

### • Monthly Aggregation

- For each transaction:

- Append to existing file or create new one
- Split multi‑month statements into correct buckets

bucket = (txn.date.year, txn.date.month)

### • Output Writer

- Writes **DEBITS** section
- Writes **CREDITS** section
- Uses naming convention:

f"{owner}{bank}{acct}{month:02d}{year}.txt"

---

# STEP‑BASED IMPLEMENTATION PLAN

## ✅ STEP 1 — Add Bank Owner Name Extraction

- Create `src/core/owner_detector.py`
- Implement bank‑specific owner detection
- Integrate into `ParsedStatement`

## ✅ STEP 2 — Add Multi‑Format Input Handler

- Create `src/core/input_handler.py`
- Detect PDF/TXT/CSV
- Normalize all formats into raw text

## ✅ STEP 3 — Create ParsedStatement Model

- Add `parsed_statement.py`
- Standardize parser output

## ✅ STEP 4 — Update All Parsers to Return ParsedStatement

- Modify AMEX + NFCU parsers
- Extract:
- debits
- credits
- statement period

## ✅ STEP 5 — Improve Account Type Detection (Bank‑Specific)

- Update `parser_detector.py`
- Use bank‑specific keyword sets
- Avoid misclassification

## ✅ STEP 6 — Monthly Aggregation Engine

- Create `src/core/aggregator.py`
- Group transactions by month
- Append or create new files

## ✅ STEP 7 — Output Writer (Debit + Credit Sections)

- Update `text_writer.py`
- Write unified monthly files
- Use naming convention

---

# END‑TO‑END FLOW

File (pdf/txt/csv)
→ load_statement()
→ detect_parser()
→ parser.parse()
→ ParsedStatement(owner, debits, credits, period)
→ group_by_month()
→ write_output_files()

---

# FUTURE ENHANCEMENTS

- Add Chase, Citi, BoA, Wells Fargo
- Add category detection (Groceries, Gas, Bills, etc.)
- Add spending analytics dashboard
- Add SQLite or DuckDB backend for long‑term storage
