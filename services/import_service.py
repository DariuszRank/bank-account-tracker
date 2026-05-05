"""
Serwis importu transakcji z plików CSV
"""

from typing import List, Dict
from parsers.citibank_parser import CitibankParser
from db.repositories import save_transaction
from models.transaction import Transaction


class ImportService:
    """
    Serwis odpowiedzialny za import transakcji z plików CSV do bazy danych
    """

    def __init__(self):
        # Słownik parserów dla różnych banków
        self.parsers = {
            'citibank': CitibankParser(),
        }

    def import_file(self, file_path: str, bank_name: str, account_name: str = None) -> Dict:
        """
        Importuje plik CSV do bazy danych

        Args:
            file_path: Ścieżka do pliku CSV
            bank_name: Nazwa banku ('citibank', 'pko', 'ing', ...)
            account_name: Nazwa konta (opcjonalnie, parser może mieć domyślną)

        Returns:
            dict: Statystyki importu {
                'total': liczba transakcji w pliku,
                'imported': liczba nowych transakcji,
                'duplicates': liczba duplikatów,
                'errors': liczba błędów
            }
        """
        # Normalizuj nazwę banku
        bank_name = bank_name.lower()

        # Sprawdź, czy mamy parser dla tego banku
        if bank_name not in self.parsers:
            raise ValueError(
                f"Brak parsera dla banku '{bank_name}'. "
                f"Dostępne banki: {', '.join(self.parsers.keys())}"
            )

        # Pobierz odpowiedni parser
        parser = self.parsers[bank_name]

        # Parsuj plik
        print(f"\n📄 Parsowanie pliku: {file_path}")
        print(f"🏦 Bank: {bank_name}")

        if account_name:
            transactions = parser.parse(file_path, account_name)
        else:
            transactions = parser.parse(file_path)

        # Importuj transakcje
        print(f"\n💾 Importowanie do bazy danych...")
        result = self._import_transactions(transactions)

        # Wyświetl podsumowanie
        self._print_summary(result)

        return result

    def _import_transactions(self, transactions: List[Transaction]) -> Dict:
        """
        Importuje listę transakcji do bazy

        Args:
            transactions: Lista obiektów Transaction

        Returns:
            dict: Statystyki importu
        """
        stats = {
            'total': len(transactions),
            'imported': 0,
            'duplicates': 0,
            'errors': 0
        }

        for transaction in transactions:
            try:
                transaction_id = save_transaction(transaction)

                if transaction_id > 0:
                    stats['imported'] += 1
                else:
                    stats['duplicates'] += 1

            except Exception as e:
                stats['errors'] += 1
                print(f"⚠ Błąd przy zapisie transakcji: {e}")
                print(f"   Transakcja: {transaction}")

        return stats

    def _print_summary(self, stats: Dict):
        """
        Wyświetla podsumowanie importu

        Args:
            stats: Statystyki importu
        """
        print("\n" + "=" * 70)
        print("📊 PODSUMOWANIE IMPORTU")
        print("=" * 70)
        print(f"Wszystkich transakcji w pliku:  {stats['total']}")
        print(f"✓ Zaimportowano nowych:         {stats['imported']}")
        print(f"⊘ Pominięto duplikatów:         {stats['duplicates']}")
        print(f"✗ Błędów:                       {stats['errors']}")
        print("=" * 70)

        if stats['imported'] > 0:
            print("✓ Import zakończony pomyślnie!")
        elif stats['duplicates'] == stats['total']:
            print("ℹ Wszystkie transakcje już istnieją w bazie")
        else:
            print("⚠ Import zakończony z błędami")

        print("=" * 70)


# Funkcja pomocnicza dla prostego użycia
def import_csv(file_path: str, bank_name: str, account_name: str = None) -> Dict:
    """
    Prosta funkcja do importu CSV

    Args:
        file_path: Ścieżka do pliku CSV
        bank_name: Nazwa banku ('citibank')
        account_name: Nazwa konta (opcjonalnie)

    Returns:
        dict: Statystyki importu
    """
    service = ImportService()
    return service.import_file(file_path, bank_name, account_name)