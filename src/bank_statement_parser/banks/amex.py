import re
from datetime import datetime
from typing import List
from interfaces.base_parser import BankStatementParser
from models.transaction import Transaction


class AmexParser(BankStatementParser):

    # Date at start of line: MM/DD/YYYY
    DATE_PATTERN = re.compile(r"^\d{1,2}/\d{2}/\d{4}")

    # Updated ID pattern: literal "ID " + exactly 15 digits
    ID_PATTERN = re.compile(r"^ID\s+\d{15}$")

    # Unlimited-size debit extraction: -$123,456.78 or - 123.45 etc.
    DEBIT_PATTERN = re.compile(r"-\s*\$?\s*([\d,]+(?:\.\d{2})?)")

    def sanitize(self, raw_text: str) -> List[str]:
        """
        Extracts only the lines between:
            MM/DD/YYYY Beginning Balance
        and
            MM/DD/YYYY Ending Balance

        Then splits that region into transaction blocks using:
            - date line = start of block
            - "ID 000000000000000" = end of block
        """
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

        start_idx = None
        end_idx = None

        # --- 1. Find the exact beginning balance line ---
        for i, line in enumerate(lines):
            if self.DATE_PATTERN.match(line) and "BEGINNING BALANCE" in line.upper():
                start_idx = i
                break

        # --- 2. Find the exact ending balance line ---
        for j in range(len(lines) - 1, -1, -1):
            if self.DATE_PATTERN.match(lines[j]) and "ENDING BALANCE" in lines[j].upper():
                end_idx = j
                break

        # If boundaries missing, nothing to parse
        if start_idx is None or end_idx is None or end_idx <= start_idx:
            return []

        # --- 3. Extract only the transaction region ---
        region = lines[start_idx + 1 : end_idx]

        # --- 4. Build transaction blocks ---
        blocks = []
        current = []
        inside_block = False

        for line in region:

            # Start of a new transaction block
            if self.DATE_PATTERN.match(line):
                inside_block = True

                # If we were already inside a block, close it
                if current:
                    blocks.append("\n".join(current))
                    current = []

                current.append(line)
                continue

            # Ignore lines until we hit the first date (header/footer noise)
            if not inside_block:
                continue

            # Append continuation lines
            current.append(line)

            # End of block = ID line
            if self.ID_PATTERN.match(line):
                blocks.append("\n".join(current))
                current = []
                inside_block = False

        if current:
            blocks.append("\n".join(current))

        return blocks


    def extract_transactions(self, blocks: List[str]) -> List[Transaction]:
        """
        Parse each block and return only DEBIT transactions.
        """
        transactions = []

        for block in blocks:
            # Only process blocks that contain a DEBIT indicator
            if not self.DEBIT_PATTERN.search(block):
                continue

            txn = self.parse_block(block)
            transactions.append(txn)

        return transactions


    def parse_block(self, block: str) -> Transaction:
        """
        Parse a single Amex transaction block.

        First line contains:
            date + description + debit/credit + running balance

        Only DEBIT transactions are included.
        """
        lines = block.splitlines()
        first = lines[0]

        # --- Extract date ---
        date_match = self.DATE_PATTERN.match(first)
        if date_match:
            date = datetime.strptime(date_match.group(0), "%m/%d/%Y").date()
        else:
            date = datetime.today().date()  # fallback date

        # --- Extract DEBIT amount (negative only, unlimited size) ---
        debit_match = self.DEBIT_PATTERN.search(first)
        if debit_match:
            raw_amount = debit_match.group(1).replace(",", "")
            amount = -float(raw_amount)
        else:
            amount = 0.0  # fallback amount

        # --- Build description ---
        desc = first

        # Remove date
        desc = re.sub(self.DATE_PATTERN, "", desc)

        # Remove debit amount
        desc = self.DEBIT_PATTERN.sub("", desc)

        # Remove trailing running balance
        desc = re.sub(r"\$?\s*[\d,]+\.\d{2}$", "", desc)

        # Add continuation lines (except the ID)
        continuation = [
            l for l in lines[1:]
            if not self.ID_PATTERN.match(l)
        ]

        description = " ".join([desc.strip()] + continuation).strip()

        # --- Always return a Transaction ---
        return Transaction(
            date=date,
            description=description,
            amount=amount
        )
