"""
Parser dla plików CSV z Citibanku
"""

import csv
import os
from datetime import datetime
from typing import List

from parsers.base_parser import BaseParser
from models.transaction import Transaction


class CitibankParser(BaseParser):
    """
    Parser dla Citibanku

    Format CSV:
    - Brak nagłówków
    - Separator: przecinek
    - Kolumny: data, opis, kwota, pusty, opis_duplikat
    - Format daty: DD/MM/YYYY
    - Format kwoty: "-143,96" (przecinek jako separator dziesiętny)
    """

    def __init__(self):
        super().__init__(platform_name='Citibank', default_currency='PLN')

    def parse(self, file_path: str, account_name: str = 'Karta kredytowa') -> List[Transaction]:
        """
        Parsuje plik CSV z Citibanku

        Args:
            file_path: Ścieżka do pliku CSV
            account_name: Nazwa konta (domyślnie "Karta kredytowa")

        Returns:
            List[Transaction]: Lista transakcji
        """
        transactions = []
        source_file = os.path.basename(file_path)

        with open(file_path, 'r', encoding='utf-8-sig') as file:
            csv_reader = csv.reader(file)

            for row_num, row in enumerate(csv_reader, start=1):
                try:
                    # Sprawdź, czy wiersz ma odpowiednią liczbę kolumn
                    if len(row) < 3:
                        print(f"⚠ Wiersz {row_num}: Za mało kolumn, pomijam")
                        continue

                    # Wyciągnij dane z kolumn
                    date_str = row[0].strip('"').strip("'")
                    description = row[1].strip('"').strip("'").strip()
                    amount_str = row[2].strip('"').strip("'")

                    # Parsuj datę
                    transaction_date = datetime.strptime(date_str, '%d/%m/%Y').date()

                    # Parsuj kwotę
                    amount = self._clean_amount(amount_str)

                    # Określ typ transakcji
                    transaction_type = 'Expense' if amount < 0 else 'Income'

                    # Określ metodę płatności
                    payment_method = self._determine_payment_method(description, amount)

                    # Utwórz obiekt Transaction
                    transaction = Transaction(
                        transaction_date=transaction_date,
                        amount=amount,
                        description=description,
                        platform_name=self.platform_name,
                        account_name=account_name,
                        currency_code=self.default_currency,
                        transaction_type=transaction_type,
                        payment_method=payment_method,
                        balance_after=None,  # Citibank nie podaje salda
                        commission=None,
                        notes=None,
                        source_file=source_file
                    )

                    transactions.append(transaction)

                except Exception as e:
                    print(f"⚠ Błąd w wierszu {row_num}: {e}")
                    print(f"   Zawartość: {row}")
                    continue

        print(f"✓ Sparsowano {len(transactions)} transakcji z pliku {source_file}")
        return transactions

    def _determine_payment_method(self, description: str, amount: float) -> str:
        """
        Określa metodę płatności na podstawie opisu i kwoty

        Args:
            description: Opis transakcji
            amount: Kwota transakcji

        Returns:
            str: Nazwa metody płatności
        """
        # Dodatnie kwoty (wpływy) to zawsze przelewy
        if amount > 0:
            return 'Przelew'

        # Ujemne kwoty (wydatki) to płatności kartą
        return 'Karta płatnicza'