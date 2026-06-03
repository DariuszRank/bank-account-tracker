"""
Parser dla plików CSV z Credit Agricole
"""

import csv
import os
from datetime import datetime
from typing import List

from parsers.base_parser import BaseParser
from models.transaction import Transaction


class CreditAgricoleParser(BaseParser):
    """
    Parser dla Credit Agricole

    Format CSV:
    - Nagłówki: TAK
    - Separator: średnik
    - Format daty: DD.MM.YYYY
    - Format kwoty: "-10,00 PLN" (przecinek, spacja, waluta)
    """

    # Mapowanie kategorii CA → payment_methods
    PAYMENT_METHOD_MAPPING = {
        'Przelew na telefon BLIK': 'Blik',
        'Płatność kartą': 'Karta płatnicza',
        'Opłata za prowadzenie rachunku': 'Inne',
        'Opłata za kartę': 'Inne',
        'Przelew zwykły': 'Przelew',
        'Polecenie zapłaty': 'Polecenie zapłaty',
        'Wypłata z bankomatu': 'Wypłata z bankomatu',
        'Opłata za wypłatę gotówki w bankomacie': 'Inne',
        'Korekta opłaty': 'Inne',
        'Płatność w Internecie BLIK': 'Blik',
        'Przelew na kartę': 'Przelew',
        'Przelew podatkowy': 'Przelew',
        'Zwrot płatności kartą': 'Karta płatnicza',
        'Przelew online': 'Przelew',
        'Zwrot płatności w Internecie BLIK': 'Blik',
        'Bonus': 'Inne',
        'Doładowanie telefonu': 'Inne',
        'Zlecenie stałe': 'Zlecenie stałe',
        'Realizacja tytułu wykonawczego': 'Inne',
        'Spłata kredytu': 'Polecenie zapłaty',
        'Wypłata z Rachunku Oszczędzam': 'Przelew',
        'Inna operacja': 'Inne',
        'Wpłata gotówkowa': 'Wpłata gotówkowa',
        'Przelew w ramach konta': 'Przelew',
    }

    def __init__(self):
        super().__init__(platform_name='Credit Agricole', default_currency='PLN')

    def parse(self, file_path: str, account_name: str = 'Konto dla Ciebie') -> List[Transaction]:
        """
        Parsuje plik CSV z Credit Agricole

        Args:
            file_path: Ścieżka do pliku CSV
            account_name: Nazwa konta

        Returns:
            List[Transaction]: Lista transakcji
        """
        transactions = []
        source_file = os.path.basename(file_path)

        with open(file_path, 'r', encoding='windows-1250') as file:
            csv_reader = csv.DictReader(file, delimiter=';')

            for row_num, row in enumerate(csv_reader, start=2):  # start=2 bo wiersz 1 to nagłówki
                try:
                    # Parsuj podstawowe dane
                    date_str = row.get('Data operacji', '').strip()
                    if not date_str:
                        continue  # Pomiń puste wiersze

                    transaction_date = datetime.strptime(date_str, '%d.%m.%Y').date()

                    # Parsuj kwotę
                    amount_str = row.get('Kwota', '').strip()
                    amount = self._parse_ca_amount(amount_str)

                    # Parsuj prowizję
                    commission_str = row.get('Prowizja', '').strip()
                    commission = self._parse_ca_commission(commission_str)

                    # Parsuj saldo
                    balance_str = row.get('Saldo po operacji', '').strip()
                    balance_after = self._parse_ca_amount(balance_str) if balance_str else None

                    # Określ opis
                    description = self._build_description(row)

                    # Określ typ transakcji
                    transaction_type = 'Expense' if amount < 0 else 'Income'

                    # Określ metodę płatności
                    category_ca = row.get('Kategoria transakcji', '').strip()
                    payment_method = self.PAYMENT_METHOD_MAPPING.get(category_ca, 'Inne')

                    # Utwórz transakcję
                    transaction = Transaction(
                        transaction_date=transaction_date,
                        amount=amount,
                        description=description,
                        platform_name=self.platform_name,
                        account_name=account_name,
                        currency_code=self.default_currency,
                        transaction_type=transaction_type,
                        payment_method=payment_method,
                        balance_after=balance_after,
                        commission=commission,
                        notes=None,
                        source_file=source_file
                    )

                    transactions.append(transaction)

                except Exception as e:
                    print(f"⚠ Błąd w wierszu {row_num}: {e}")
                    continue

        print(f"✓ Sparsowano {len(transactions)} transakcji z pliku {source_file}")
        return transactions

    def _parse_ca_amount(self, amount_str: str) -> float:
        """
        Parsuje kwotę Credit Agricole

        Format: "-10,00 PLN" lub "1 234,56 PLN" lub z non-breaking space

        Args:
            amount_str: String z kwotą

        Returns:
            float: Kwota jako liczba
        """
        if not amount_str:
            return 0.0

        # Usuń "PLN", "EUR", "USD" itp.
        amount_str = amount_str.replace('PLN', '').replace('EUR', '').replace('USD', '')
        amount_str = amount_str.strip()

        # Usuń wszystkie spacje (w tym non-breaking space \xa0)
        amount_str = amount_str.replace(' ', '')
        amount_str = amount_str.replace('\xa0', '')  # Non-breaking space
        amount_str = amount_str.replace('\u00a0', '')  # Unicode non-breaking space

        # Zamień przecinek na kropkę
        amount_str = amount_str.replace(',', '.')

        try:
            return float(amount_str)
        except ValueError:
            # Dodatkowe czyszczenie na wszelki wypadek
            import re
            # Usuń wszystkie znaki nie będące cyframi, kropką, minusem
            cleaned = re.sub(r'[^0-9.\-]', '', amount_str)
            return float(cleaned)

    def _parse_ca_commission(self, commission_str: str) -> float:
        """
        Parsuje prowizję Credit Agricole

        Prowizja w CA jest BEZ znaku ujemnego, ale zmniejsza saldo.
        Zwracamy ją jako wartość ujemną.

        Args:
            commission_str: String z prowizją

        Returns:
            float: Prowizja jako liczba ujemna (lub 0 jeśli brak)
        """
        if not commission_str or commission_str == '0,00 PLN':
            return 0.0

        amount = self._parse_ca_amount(commission_str)

        # Prowizja zawsze zmniejsza saldo, więc zwracamy wartość ujemną
        return -abs(amount)

    def _build_description(self, row: dict) -> str:
        """
        Buduje opis transakcji z dostępnych pól

        Priorytet:
        1. Miejsce transakcji (dla płatności kartą)
        2. Tytuł (dla przelewów)
        3. Nadawca (dla wpływów)
        4. Odbiorca (dla wypływów)
        5. Kategoria transakcji (fallback)

        Args:
            row: Wiersz CSV jako słownik

        Returns:
            str: Opis transakcji
        """
        miejsce = row.get('Miejsce transakcji', '').strip()
        tytul = row.get('Tytuł', '').strip()
        nadawca = row.get('Nadawca', '').strip()
        odbiorca = row.get('Odbiorca', '').strip()
        kategoria = row.get('Kategoria transakcji', '').strip()

        # 1. Miejsce transakcji (płatności kartą, bankomaty)
        if miejsce:
            return miejsce

        # 2. Tytuł przelewu
        if tytul:
            # Jeśli jest nadawca lub odbiorca, dodaj go
            if nadawca:
                return f"{nadawca}: {tytul}"
            elif odbiorca:
                return f"{odbiorca}: {tytul}"
            return tytul

        # 3. Nadawca (wpływy)
        if nadawca:
            return nadawca

        # 4. Odbiorca (wypływy)
        if odbiorca:
            return odbiorca

        # 5. Kategoria (fallback)
        return kategoria if kategoria else 'Brak opisu'