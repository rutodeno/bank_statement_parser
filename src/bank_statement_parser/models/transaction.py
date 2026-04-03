from dataclasses import dataclass
from datetime import date

@dataclass
class Transaction:
    date: date
    description: str
    amount: float

    def __post_init__(self):
        # Normalize description
        self.description = self.description.strip()

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "description": self.description,
            "amount": self.amount,
        }
