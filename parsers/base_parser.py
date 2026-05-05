"""
Klasa bazowa dla wszystkich parserów banków
"""

from abc import ABC, abstractmethod
from typing import List
from models.transaction import Transaction


class BaseParser(ABC):
    """
    Klasa abstrakcyjna definiująca interfejs parsera

    Każdy parser dla konkretnego banku dziedziczy po tej klasie
    i implementuje metodę parse()
    """

    def __init__(self, platform_name: str, default_currency: str = 'PLN'):
        """
        Args:
            platform_name: Nazwa banku/platformy
            default_currency: Domyślna waluta (jeśli nie ma w pliku)
        """
        self.platform_name = platform_name
        self.default_currency = default_currency

    @abstractmethod
    def parse(self, file_path: str, account_name: str) -> List[Transaction]:
        """
        Parsuje plik CSV i zwraca listę transakcji

        Args:
            file_path: Ścieżka do pliku CSV
            account_name: Nazwa konta (np. "Karta kredytowa")

        Returns:
            List[Transaction]: Lista obiektów Transaction
        """
        pass

    def _clean_amount(self, amount_str: str) -> float:
        """
        Czyści i konwertuje kwotę na float

        Przykłady:
            "-143,96" -> -143.96
            "1 234,56" -> 1234.56
            "1.234,56" -> 1234.56
        """
        # Usuń cudzysłowy
        amount_str = amount_str.strip('"').strip("'")

        # Usuń spacje
        amount_str = amount_str.replace(' ', '')

        # Zamień przecinek na kropkę (separator dziesiętny)
        amount_str = amount_str.replace(',', '.')

        # Usuń kropki jako separatory tysięcy (jeśli są)
        # Ale tylko jeśli jest więcej niż jedna kropka
        parts = amount_str.split('.')
        if len(parts) > 2:
            # Ostatnia kropka to separator dziesiętny
            amount_str = ''.join(parts[:-1]) + '.' + parts[-1]

        return float(amount_str)