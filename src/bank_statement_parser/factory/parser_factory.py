from banks.navy_federal import NavyFederalParser
from banks.amex import AmexParser

class ParserFactory:

    @staticmethod
    def get_parser(raw_text: str):
        text = raw_text.upper()

        if "NAVY FEDERAL" in text:
            return NavyFederalParser()

        if "AMERICAN EXPRESS" in text or "AMEX" in text:
            return AmexParser()

        raise ValueError("No parser found for this bank")
