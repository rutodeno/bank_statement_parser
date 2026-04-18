import re
from typing import Optional
from factory.parser_detector import Bank


def extract_owner_name(text: str, bank: Bank) -> str:
    """
    Extracts the account owner's name from the statement text.
    Uses bank‑specific rules for higher accuracy.
    Returns 'unknown' if no name can be confidently detected.
    """
    t = text.strip()

    if bank == Bank.AMEX:
        name = _extract_amex_owner(t)
        if name:
            return name

    if bank == Bank.NAVY_FEDERAL:
        name = _extract_nfcu_owner(t)
        if name:
            return name

    # Fallback: try generic name detection
    name = _extract_generic_name(t)
    return name or "unknown"


# ---------------------------------------------------------
# AMEX OWNER DETECTION
# ---------------------------------------------------------

def _extract_amex_owner(text: str) -> Optional[str]:
    """
    AMEX statements typically show the owner name in the header block,
    often above the 'Account Ending:' line.
    """

    lines = text.splitlines()

    # 1. Look for "Account Ending:" (new pattern)
    for i, line in enumerate(lines):
        if "ACCOUNT ENDING:" in line.upper():
            # Owner name is usually 1–3 lines above
            for j in range(i - 3, i):
                if j >= 0 and _looks_like_name(lines[j]):
                    return lines[j].strip()

    # 2. Look for uppercase name near the top of the document
    header = lines[:20]
    for line in header:
        if _looks_like_name(line):
            return line.strip()

    return None


# ---------------------------------------------------------
# NFCU OWNER DETECTION
# ---------------------------------------------------------

def _extract_nfcu_owner(text: str) -> Optional[str]:
    """
    NFCU statements often contain:
        'TOTAL New Activity for JOHN DOE'
        'Member: JOHN DOE'
        'Primary Owner: JOHN DOE'
    """

    # 1. TOTAL New Activity for <NAME>
    match = re.search(r"TOTAL NEW ACTIVITY FOR\s+([A-Z][A-Z\s\-']+)", text.upper())
    if match:
        return match.group(1).title()

    # 2. Member: <NAME>
    match = re.search(r"MEMBER:\s+([A-Z][A-Z\s\-']+)", text.upper())
    if match:
        return match.group(1).title()

    # 3. Primary Owner: <NAME>
    match = re.search(r"PRIMARY OWNER:\s+([A-Z][A-Z\s\-']+)", text.upper())
    if match:
        return match.group(1).title()

    # 4. OWNER: <NAME>
    match = re.search(r"OWNER:\s+([A-Z][A-Z\s\-']+)", text.upper())
    if match:
        return match.group(1).title()

    # 5. Header block fallback
    lines = text.splitlines()[:20]
    for line in lines:
        if _looks_like_name(line):
            return line.strip()

    return None


# ---------------------------------------------------------
# GENERIC FALLBACK
# ---------------------------------------------------------

def _extract_generic_name(text: str) -> Optional[str]:
    """
    Fallback for unknown banks.
    Looks for a standalone uppercase name in the header.
    """

    lines = text.splitlines()[:20]

    for line in lines:
        if _looks_like_name(line):
            return line.strip()

    return None


# ---------------------------------------------------------
# NAME HEURISTICS
# ---------------------------------------------------------

def _looks_like_name(line: str) -> bool:
    """
    Heuristic to detect if a line looks like a person's name.
    Rules:
        - 1–4 words
        - Mostly alphabetic
        - Uppercase or Title Case
        - No digits
    """

    cleaned = line.strip()

    if not cleaned:
        return False

    # Ignore lines with digits (addresses, account numbers)
    if any(char.isdigit() for char in cleaned):
        return False

    words = cleaned.split()
    if not (1 <= len(words) <= 4):
        return False

    # Accept uppercase names
    if cleaned.isupper():
        return True

    # Accept Title Case names
    if all(w[0].isupper() for w in words if w):
        return True

    return False
