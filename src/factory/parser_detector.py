"""
Detects the bank (Amex, NFCU) and the account type (checking vs credit card),
then returns the correct parser instance.
"""

from enum import Enum
from typing import Type

from banks.navy_federal.nfcu_credit import NFCUCreditParser
from banks.navy_federal.nfcu_debit import NFCUDebitParser
from banks.amex.amex_debit import AmexDebitParser
from banks.amex.amex_credit import AmexCreditParser


# ---------------------------------------------------------
# ENUMS
# ---------------------------------------------------------

class Bank(Enum):
    AMEX = "amex"
    NAVY_FEDERAL = "navy_federal"
    UNKNOWN = "unknown"


class AccountType(Enum):
    CHECKING = "checking"
    CREDIT_CARD = "credit_card"
    UNKNOWN = "unknown"


# ---------------------------------------------------------
# 1. HIGH‑CONFIDENCE BANK DETECTION
# ---------------------------------------------------------

def detect_bank(text: str) -> Bank:
    """
    Detects the bank using strong, unique identifiers.
    Uses header detection first, then signal scoring.
    """
    t = text.upper()
    header = t[:300]  # first 300 chars usually contain the statement header

    # --- Strong header detection ---
    if "NAVY FEDERAL CREDIT UNION" in header:
        return Bank.NAVY_FEDERAL

    if "AMERICAN EXPRESS" in header:
        return Bank.AMEX

    # --- Secondary signal scoring ---
    amex_signals = [
        "AMERICAN EXPRESS",
        "MEMBERSHIP REWARDS",
        "BLUE CASH",
        "STATEMENT CLOSING DATE",
        "AMEX®",
    ]

    nfcu_signals = [
        "NAVY FEDERAL",
        "NFCU",
        "NAVY FEDERAL ONLINE",
        "NAVY FEDERAL CREDIT CARD",
        "NAVY FEDERAL CHECKING",
    ]

    amex_hits = sum(s in t for s in amex_signals)
    nfcu_hits = sum(s in t for s in nfcu_signals)

    if amex_hits > nfcu_hits and amex_hits > 0:
        return Bank.AMEX

    if nfcu_hits > amex_hits and nfcu_hits > 0:
        return Bank.NAVY_FEDERAL

    return Bank.UNKNOWN


# ---------------------------------------------------------
# 2. BANK‑SPECIFIC ACCOUNT TYPE DETECTION
# ---------------------------------------------------------

def detect_account_type(text: str, bank: Bank) -> AccountType:
    t = text.upper()

    if bank == Bank.AMEX:
        return _detect_account_type_amex(t)

    if bank == Bank.NAVY_FEDERAL:
        return _detect_account_type_nfcu(t)

    return AccountType.UNKNOWN


def _detect_account_type_amex(t: str) -> AccountType:
    credit_signals = [
        "MINIMUM PAYMENT DUE",
        "PAYMENT DUE DATE",
        "NEW BALANCE",
        "PREVIOUS BALANCE",
        "CREDIT LIMIT",
        "AVAILABLE CREDIT",
        "INTEREST CHARGES",
        "FEES",
        "REWARDS SUMMARY",
    ]

    checking_signals = [
        "BEGINNING BALANCE",
        "ENDING BALANCE",
        "AVAILABLE BALANCE",
        "DEPOSITS",
        "WITHDRAWALS",
        "ROUTING NUMBER",
        "CHECKING ACCOUNT",
        "AMERICAN EXPRESS® CHECKING",
    ]

    if any(s in t for s in credit_signals):
        return AccountType.CREDIT_CARD

    if any(s in t for s in checking_signals):
        return AccountType.CHECKING

    return AccountType.UNKNOWN


def _detect_account_type_nfcu(t: str) -> AccountType:
    credit_signals = [
        "CREDIT CARD STATEMENT",
        "MINIMUM PAYMENT DUE",
        "PAYMENT DUE DATE",
        "NEW BALANCE",
        "CREDIT LIMIT",
    ]

    checking_signals = [
        "CHECKING ACCOUNT",
        "CHECKING SUMMARY",
        "SHARE DRAFT",
        "DEPOSITS AND WITHDRAWALS",
        "CHECKING ACCOUNT SUMMARY",
    ]

    if any(s in t for s in credit_signals):
        return AccountType.CREDIT_CARD

    if any(s in t for s in checking_signals):
        return AccountType.CHECKING

    return AccountType.UNKNOWN


# ---------------------------------------------------------
# 3. ROUTING TABLE
# ---------------------------------------------------------

PARSER_MAP = {
    (Bank.AMEX, AccountType.CHECKING): AmexDebitParser,
    (Bank.AMEX, AccountType.CREDIT_CARD): AmexCreditParser,
    (Bank.NAVY_FEDERAL, AccountType.CHECKING): NFCUDebitParser,
    (Bank.NAVY_FEDERAL, AccountType.CREDIT_CARD): NFCUCreditParser,
}


# ---------------------------------------------------------
# 4. MAIN ENTRY POINT
# ---------------------------------------------------------

def detect_parser(text: str):
    bank = detect_bank(text)
    acct = detect_account_type(text, bank)

    key = (bank, acct)

    if key in PARSER_MAP:
        parser_class = PARSER_MAP[key]
        print(f"Detected: {bank.value} / {acct.value}")
        return parser_class()

    raise ValueError(
        f"Unable to detect parser for bank={bank.value}, account={acct.value}"
    )