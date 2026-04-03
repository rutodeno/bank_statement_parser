from interfaces.base_parser import BankStatementParser
from models.transaction import Transaction
from datetime import datetime
from typing import List
import re

class NavyFederalParser(BankStatementParser):

    def sanitize(self, raw_text: str) -> List[str]:
        cleaned_lines = []
        skip_payments = False

        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue

            if "PAYMENTS AND CREDITS" in line:
                skip_payments = not skip_payments

            # we skip the credit section
            if skip_payments:
                continue

            # Keep only real transaction lines (MM/DD/YY)
            if re.match(r"^\d{2}/\d{2}/\d{2}", line):
                cleaned_lines.append(line)

        return cleaned_lines


    def extract_transactions(self, blocks: List[str]) -> List[Transaction]:
        transactions = []

        pattern = (
            r"(\d{2}/\d{2}/\d{2})\s+"        # trans date
            r"(\d{2}/\d{2}/\d{2})\s+"        # post date
            r"(\d+)\s+"                      # reference number
            r"(.*?)\s+"                      # description
            r"\$?(-?\d+\.\d{2})$"            # amount (optional $)
        )

        for line in blocks:
            match = re.match(pattern, line)
            if not match:
                continue

            trans_date, post_date, ref, desc, amount = match.groups()

            transactions.append(
                Transaction(
                    date=datetime.strptime(trans_date, "%m/%d/%y").date(),
                    description=desc.strip(),
                    amount=float(amount)
                )
            )

        return transactions
