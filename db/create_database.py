"""
Skrypt tworzący bazę danych dla aplikacji finansowej.
Uruchom raz: python create_database.py
Utworzy plik: finance.db
"""

import sqlite3
import os
import sys

# Dodaj ścieżkę do głównego katalogu projektu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATABASE_PATH


def create_database():
    """Tworzy bazę danych z wszystkimi tabelami i danymi początkowymi"""

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    # ========== TWORZENIE TABEL ==========

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platforms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,                  -- PKO BP, Revolut, ING, Millenium
            is_active BOOLEAN DEFAULT 1
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS currencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,                  -- PLN, EUR, USD, CHF, NOK, BGN
            name TEXT NOT NULL,                         -- Polski Złoty, Euro, Dolar
            symbol TEXT                                 -- zł, €, $, CHF, kr, лв
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_id INTEGER NOT NULL,
            account_name TEXT NOT NULL,                 -- Revolut PLN, Revolut EUR, Przekorzystne 
            account_type TEXT,                          -- ROR, Oszczędnościowe, Walutowe
            account_number TEXT,                        -- 12****789 (maskowany numer do matchowania przelewów)
            currency_id INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (platform_id) REFERENCES platforms(id),
            FOREIGN KEY (currency_id) REFERENCES currencies(id),
            UNIQUE(platform_id, account_name)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaction_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE                   -- Expense, Income, Transfer Send,
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE                   -- Blik, Karta płatnicza, Przelew, 
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            transaction_date DATETIME NOT NULL,
            transaction_type_id INTEGER NOT NULL,
            payment_method_id INTEGER,
            amount DECIMAL(15, 2) NOT NULL,
            commission DECIMAL(15, 2) DEFAULT 0,
            currency_id INTEGER NOT NULL,
            category_id INTEGER,
            description TEXT,
            balance_after DECIMAL(15, 2),
            notes TEXT,
            source_file TEXT,
            import_hash TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (transaction_type_id) REFERENCES transaction_types(id),
            FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
            FOREIGN KEY (currency_id) REFERENCES currencies(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
    """)

    # Indeksy
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_hash ON transactions(import_hash);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_platform ON accounts(platform_id);")

    # ========== WYPEŁNIANIE SŁOWNIKÓW ==========

    currencies = [
        ('PLN', 'Polski Złoty', 'zł'),
        ('EUR', 'Euro', '€'),
        ('USD', 'Dolar Amerykański', '$'),
        ('CHF', 'Frank Szwajcarski', 'CHF'),
        ('GBP', 'Funt Brytyjski', '£'),
        ('NOK', 'Korona Norweska', 'kr'),
        ('BGN', 'Lew Bułgarski', 'лв'),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO currencies (code, name, symbol) VALUES (?, ?, ?)",
        currencies
    )

    transaction_types = [
        ('Expense',),
        ('Income',),
        ('Transfer Send',),
        ('Transfer Deposit',),
        ('Cash Exchange (Sell)',),
        ('Cash Exchange (Buy)',),
        ('Starting Balance',),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO transaction_types (name) VALUES (?)",
        transaction_types
    )

    payment_methods = [
        ('Blik',),
        ('Karta płatnicza',),
        ('Przelew',),
        ('Wypłata z bankomatu',),
        ('Wymiana walut',),
        ('Gotówka',),
        ('Polecenie zapłaty',),
        ('Zlecenie stałe',),
        ('Wpłata gotówkowa',),
        ('Inne',),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO payment_methods (name) VALUES (?)",
        payment_methods
    )

    categories = [
        ('Paliwo w skały',),
        ('Wymiana walut',),
        ('Inne',),
        ('Artykuły Spożywcze',),
        ('Transport',),
        ('Telefon',),
        ('Fryzjer',),
        ('Jedzenie na mieście',),
        ('Gaz',),
        ('Czynsz',),
        ('Darowizny',),
        ('Rozliczenie wydatków',),
        ('Wynagrodzenie',),
        ('Wakacje',),
        ('Prąd',),
        ('Odsetki',),
        ('Prezenty',),
        ('Kredyt Hipoteczny',),
        ('Lunch Teamowy',),
        ('Narty',),
        ('Rozrywka',),
        ('Wspinaczkowe poza paliwem',),
        ('Dopłata do ściany',),
        ('Zdrowie',),
        ('Turystyka',),
        ('Remont/Mieszkanie',),
        ('Auto',),
        ('Dziecko',),
        ('Promocje bankowe',),
        ('Prowizje bankowe',),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO categories (name) VALUES (?)",
        categories
    )

    conn.commit()
    conn.close()

    print("✓ Baza danych została utworzona pomyślnie!")

if __name__ == '__main__':
    create_database()