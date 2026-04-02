'''
Remove any sensitive information. Only keep transaction data - Date, item and amount
'''
import re

DATE_REGEX = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}/\d{1,2}|\d{4}-\d{2}-\d{2})")

def sanitize_text(raw_text: str) -> list[str]:
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    cleaned = []

    for i, line in enumerate(lines):
        if DATE_REGEX.match(line):
            cleaned.append(line)
            # include following lines until next date
            j = i + 1
            while j < len(lines) and not DATE_REGEX.match(lines[j]):
                cleaned.append(lines[j])
                j += 1

    return cleaned