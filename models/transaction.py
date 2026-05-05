"""
Model transakcji
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Transaction:
    """
    Reprezentuje pojedynczą transakcję finansową

    To jest prosty model danych, który będzie używany przez:
    - parsery (do zwracania sparsowanych transakcji)
    - import service (do zapisywania do bazy)
    - analizy (do pracy z danymi)
    """

    # Podstawowe dane
    transaction_date: date
    amount: float
    description: str

    # Powiązania (nazwy lub ID)
    platform_name: str
    account_name: str
    currency_code: str
    transaction_type: str

    # Opcjonalne dane
    payment_method: Optional[str] = None
    category_name: Optional[str] = None
    balance_after: Optional[float] = None
    notes: Optional[str] = None
    source_file: Optional[str] = None

    # ID z bazy (wypełniane po zapisie)
    id: Optional[int] = None
    account_id: Optional[int] = None
    currency_id: Optional[int] = None
    transaction_type_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    category_id: Optional[int] = None

    def __str__(self):
        """Czytelna reprezentacja transakcji"""
        return (f"{self.transaction_date} | {self.amount:>10.2f} {self.currency_code} | "
                f"{self.description[:50]}")

    def to_dict(self):
        """Konwertuje transakcję do słownika (przydatne przy exportach)"""
        return {
            'date': self.transaction_date.isoformat() if self.transaction_date else None,
            'amount': self.amount,
            'description': self.description,
            'platform': self.platform_name,
            'account': self.account_name,
            'currency': self.currency_code,
            'type': self.transaction_type,
            'payment_method': self.payment_method,
            'category': self.category_name,
            'balance_after': self.balance_after,
            'notes': self.notes,
        }