from abc import ABC, abstractmethod
from typing import List
from models.transaction import Transaction


class BankStatementParser(ABC):

    @abstractmethod
    def sanitize(self, raw_text: str) -> list[str]:
        """Remove noise (header, footer, ads, blank lines)"""
        pass

    @abstractmethod
    def extract_transactions(self, blocks: list[str]) -> List[Transaction]:
        """Return structured transactions."""
        pass

    def parse(self, raw_text: str) -> List[Transaction]:
        cleaned = self.sanitize(raw_text)
        return self.extract_transactions(cleaned)
