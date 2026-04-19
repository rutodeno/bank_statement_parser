import re
from datetime import datetime
from typing import List
from interfaces.base_parser import BankStatementParser
from models.transaction import Transaction


class AmexCreditParser(BankStatementParser):

    # ---------------------------------------------------------
    # 1. SANITIZE — Extract only the "Total New Charges" section
    # ---------------------------------------------------------
    def sanitize(self, raw_text: str) -> List[str]:
        """
        Extract only the 'Total New Charges' section.
        Keep all lines inside that section so we can test
        whether the extractor outputs single-line transactions.
        """
        lines = []
        in_new_charges = False

        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue

            # Start of the section we care about
            if "TOTAL NEW CHARGES" in line.upper():
                in_new_charges = True
                continue

            # End of section (AMEX usually has FEES or INTEREST next)
            if in_new_charges and line.upper().startswith(("FEES", "INTEREST")):
                break

            if in_new_charges:
                lines.append(line)

        return lines

    # ---------------------------------------------------------
    # 2. EXTRACT TRANSACTIONS — Single-line regex parsing
    # ---------------------------------------------------------
    def extract_transactions(self, blocks: List[str]) -> List[Transaction]:
        """
        Parse single-line AMEX transactions using regex.
        Expected format:
            MM/DD/YY DESCRIPTION LOCATION STATE AMOUNT
        Example:
            01/12/25 UBER TRIP HELP.UBER.COM AMZN.COM/BILL CA 23.45
        """
        transactions = []

        pattern = (
            r"^(\d{2}/\d{2}/\d{2})\s+"      # date
            r"(.*?)\s+"                     # description (lazy)
            r"\$?(\d+\.\d{2})$"             # amount (with or without $)
        )

        for line in blocks:
            match = re.match(pattern, line)
            if not match:
                continue

            trans_date_str, description, amount_str = match.groups()

            transactions.append(
                Transaction(
                    date=datetime.strptime(trans_date_str, "%m/%d/%y").date(),
                    description=description.strip(),
                    amount=-float(amount_str)  # charges are negative
                )
            )
        return transactions
