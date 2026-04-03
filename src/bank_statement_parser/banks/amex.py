import re
from datetime import datetime
from interfaces.base_parser import BankStatementParser
from models.transaction import Transaction
from typing import List


class AmexParser(BankStatementParser):

    DATE_PATTERN = r"^\d{2}/\d{2}/\d{4}"

    def sanitize(self, raw_text: str) -> list[str]:
        lines = [line.rstrip() for line in raw_text.splitlines()]
        blocks = []
        current = []

        for line in lines:
            if re.match(self.DATE_PATTERN, line) and current:
                    blocks.append("\n".join(current))
                    current = []
            if line.strip():
                current.append(line)

        if current:
            blocks.append("\n".join(current))

        return blocks

    def extract_transactions(self, blocks):
        transactions = []
        for block in blocks:
            try:
                transactions.append(self.parse_block(block))
            except ValueError:
                continue  # skip invalid blocks
        return transactions


    def parse_block(self, block: str) -> Transaction:
        lines = block.splitlines()

        # 1. Extract date
        date_match = re.match(r"(\d{2}/\d{2}/\d{4})", lines[0])
        if not date_match:
            raise ValueError("Invalid block: missing date")

        date = datetime.strptime(date_match.group(1), "%m/%d/%Y").date()

        # 2. Extract amount
        amount = None
        for line in lines:
            match = re.search(r"([-+]?\d+\.?\d+)", line)
            if match:
                amount = float(match.group(1))
                break

        if amount is None:
            raise ValueError("Invalid block: missing amount")

        # 3. Description
        description = " ".join(line.strip() for line in lines[1:])

        return Transaction(date=date, description=description, amount=amount)