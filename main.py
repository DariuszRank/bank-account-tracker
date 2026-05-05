"""
Główny plik aplikacji Finance Tracker
"""

from config import DATABASE_PATH


def main():
    """Główna funkcja aplikacji"""
    print("=" * 50)
    print("Finance Tracker - wersja robocza")
    print("=" * 50)
    print(f"Baza danych: {DATABASE_PATH}")
    print("\nAplikacja gotowa do rozbudowy!")
    print("=" * 50)


if __name__ == '__main__':
    main()