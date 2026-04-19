import re
from datetime import datetime
from typing import List
from interfaces.base_parser import BankStatementParser
from models.transaction import Transaction


class NFCUDebitParser(BankStatementParser):

    # Transaction date pattern: MM-DD
    DATE_PATTERN = re.compile(r"^(\d{2})-(\d{2})")

    # Full Statement Period block:
    # Statement Period
    # 12/20/24 - 01/19/25
    PERIOD_PATTERN = re.compile(
        r"Statement Period\s+"
        r"(\d{2})/(\d{2})/(\d{2})\s*-\s*"
        r"(\d{2})/(\d{2})/(\d{2})"
    )

    # Predeclare attributes so Pylance knows they are always ints
    start_month: int = 0
    start_year: int = 0
    end_month: int = 0
    end_year: int = 0

    def sanitize(self, raw_text: str) -> List[str]:
        """
        Extract all lines between:
            MM-DD Beginning Balance
        and
            MM-DD Ending Balance

        Also extract the statement period so we can infer the year.
        """
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

        # --- Extract statement period (for year inference) ---
        for i, line in enumerate(lines):
            if "STATEMENT PERIOD" in line.upper() and i + 1 < len(lines):
                block = line + " " + lines[i + 1]
                m = self.PERIOD_PATTERN.search(block)
                if m:
                    # Start period
                    self.start_month = int(m.group(1))
                    self.start_year = 2000 + int(m.group(3))

                    # End period
                    self.end_month = int(m.group(4))
                    self.end_year = 2000 + int(m.group(6))
                break

        extracted = []
        in_section = False

        for line in lines:

            # Start of a section
            if self.DATE_PATTERN.match(line) and "BEGINNING BALANCE" in line.upper():
                in_section = True
                continue

            # End of a section
            if in_section and self.DATE_PATTERN.match(line) and "ENDING BALANCE" in line.upper():
                in_section = False
                continue

            # Collect lines inside sections
            if in_section:
                extracted.append(line)

        return extracted

    # ---------------------------------------------------------
    # 2. EXTRACT TRANSACTIONS — Single-line regex parsing
    # ---------------------------------------------------------
    def extract_transactions(self, blocks: List[str]) -> List[Transaction]:
        """
        Parse single-line NFCU debit transactions using regex.
        Expected format:
            MM-DD DESCRIPTION AMOUNT BALANCE
        Example:
            12-30 Deposit - ACH Paid From Microsoft Edipayment 01Afd9 3,027.73 8,816.39
        """
        transactions = []

        pattern = (
            r"^(\d{2})-(\d{2})\s+"        # month-day
            r"(.*?)\s+"                   # description
            r"(-?[\d,]+\.\d{2}-?)\s+"     # amount (with commas)
            r"[\d,]+\.\d{2}$"             # trailing balance (ignored)
        )

        for line in blocks:
            match = re.match(pattern, line)
            if not match:
                continue

            month_str, day_str, description, amount_str = match.groups()

            month = int(month_str)
            day = int(day_str)

            # Infer year from statement period
            if month == self.start_month:
                year = self.start_year
            else:
                year = self.end_year

            date = datetime(year, month, day).date()

            # Clean amount (remove commas, handle trailing '-')
            clean_amount = amount_str.replace(",", "")
            if clean_amount.endswith("-"):
                amount = -float(clean_amount[:-1])
            else:
                amount = float(clean_amount)

            transactions.append(
                Transaction(
                    date=date,
                    description=description.strip(),
                    amount=amount
                )
            )

        return transactions
