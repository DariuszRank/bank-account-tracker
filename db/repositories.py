"""
Repozytorium - funkcje do pobierania i zapisywania danych
"""

from db.connection import execute_query, execute_insert
from typing import Optional


# ========== PLATFORMS ==========

def get_platform_by_name(name: str) -> Optional[dict]:
    """
    Pobiera platformę po nazwie

    Args:
        name: Nazwa platformy (np. 'PKO BP', 'Revolut')

    Returns:
        dict lub None: Słownik z danymi platformy {'id': 1, 'name': 'PKO BP', 'is_active': 1}
    """
    query = "SELECT id, name, is_active FROM platforms WHERE name = ?"
    results = execute_query(query, (name,))

    if results:
        row = results[0]
        return dict(row)
    return None


def create_platform(name: str) -> int:
    """
    Tworzy nową platformę

    Args:
        name: Nazwa platformy

    Returns:
        int: ID nowo utworzonej platformy
    """
    query = "INSERT INTO platforms (name, is_active) VALUES (?, 1)"
    return execute_insert(query, (name,))


def get_or_create_platform(name: str) -> int:
    """
    Pobiera ID platformy lub tworzy nową, jeśli nie istnieje

    Args:
        name: Nazwa platformy

    Returns:
        int: ID platformy
    """
    platform = get_platform_by_name(name)
    if platform:
        return platform['id']
    return create_platform(name)


# ========== CURRENCIES ==========

def get_currency_by_code(code: str) -> Optional[dict]:
    """
    Pobiera walutę po kodzie

    Args:
        code: Kod waluty (np. 'PLN', 'EUR')

    Returns:
        dict lub None: Słownik z danymi waluty
    """
    query = "SELECT id, code, name, symbol FROM currencies WHERE code = ?"
    results = execute_query(query, (code,))

    if results:
        row = results[0]
        return dict(row)
    return None


def get_currency_id(code: str) -> Optional[int]:
    """
    Pobiera ID waluty po kodzie

    Args:
        code: Kod waluty

    Returns:
        int lub None: ID waluty
    """
    currency = get_currency_by_code(code)
    return currency['id'] if currency else None


# ========== ACCOUNTS ==========

def get_account_by_name(platform_id: int, account_name: str) -> Optional[dict]:
    """
    Pobiera konto po nazwie i platformie

    Args:
        platform_id: ID platformy
        account_name: Nazwa konta

    Returns:
        dict lub None: Słownik z danymi konta
    """
    query = """
        SELECT id, platform_id, account_name, account_type, 
               account_number, currency_id, is_active 
        FROM accounts 
        WHERE platform_id = ? AND account_name = ?
    """
    results = execute_query(query, (platform_id, account_name))

    if results:
        row = results[0]
        return dict(row)
    return None


def create_account(platform_id: int, account_name: str, currency_id: int,
                   account_type: str = None, account_number: str = None) -> int:
    """
    Tworzy nowe konto

    Args:
        platform_id: ID platformy
        account_name: Nazwa konta
        currency_id: ID waluty
        account_type: Typ konta (opcjonalnie)
        account_number: Numer konta (opcjonalnie)

    Returns:
        int: ID nowo utworzonego konta
    """
    query = """
        INSERT INTO accounts (platform_id, account_name, currency_id, account_type, account_number, is_active)
        VALUES (?, ?, ?, ?, ?, 1)
    """
    return execute_insert(query, (platform_id, account_name, currency_id, account_type, account_number))


def get_or_create_account(platform_name: str, account_name: str, currency_code: str,
                          account_type: str = None, account_number: str = None) -> int:
    """
    Pobiera ID konta lub tworzy nowe, jeśli nie istnieje

    Args:
        platform_name: Nazwa platformy
        account_name: Nazwa konta
        currency_code: Kod waluty
        account_type: Typ konta (opcjonalnie)
        account_number: Numer konta (opcjonalnie)

    Returns:
        int: ID konta
    """
    platform_id = get_or_create_platform(platform_name)
    currency_id = get_currency_id(currency_code)

    if not currency_id:
        raise ValueError(f"Waluta {currency_code} nie istnieje w bazie danych")

    account = get_account_by_name(platform_id, account_name)
    if account:
        return account['id']

    return create_account(platform_id, account_name, currency_id, account_type, account_number)


# ========== TRANSACTION TYPES ==========

def get_transaction_type_by_name(name: str) -> Optional[dict]:
    """Pobiera typ transakcji po nazwie"""
    query = "SELECT id, name FROM transaction_types WHERE name = ?"
    results = execute_query(query, (name,))

    if results:
        return dict(results[0])
    return None


def get_transaction_type_id(name: str) -> Optional[int]:
    """Pobiera ID typu transakcji"""
    trans_type = get_transaction_type_by_name(name)
    return trans_type['id'] if trans_type else None


# ========== PAYMENT METHODS ==========

def get_payment_method_by_name(name: str) -> Optional[dict]:
    """Pobiera metodę płatności po nazwie"""
    query = "SELECT id, name FROM payment_methods WHERE name = ?"
    results = execute_query(query, (name,))

    if results:
        return dict(results[0])
    return None


def get_payment_method_id(name: str) -> Optional[int]:
    """Pobiera ID metody płatności"""
    method = get_payment_method_by_name(name)
    return method['id'] if method else None


# ========== CATEGORIES ==========

def get_category_by_name(name: str) -> Optional[dict]:
    """Pobiera kategorię po nazwie"""
    query = "SELECT id, name FROM categories WHERE name = ?"
    results = execute_query(query, (name,))

    if results:
        return dict(results[0])
    return None


def get_category_id(name: str) -> Optional[int]:
    """Pobiera ID kategorii"""
    category = get_category_by_name(name)
    return category['id'] if category else None


def get_all_categories() -> list:
    """Pobiera wszystkie kategorie"""
    query = "SELECT id, name FROM categories ORDER BY name"
    results = execute_query(query)
    return [dict(row) for row in results]


# ========== TRANSACTIONS ==========

import hashlib
from models.transaction import Transaction


def generate_import_hash(transaction: Transaction, account_id: int) -> str:
    """
    Generuje unikalny hash dla transakcji (ochrona przed duplikatami)

    Hash bazuje na:
    - account_id
    - data transakcji
    - kwota
    - opis
    - saldo po transakcji (jeśli dostępne)

    Args:
        transaction: Obiekt Transaction
        account_id: ID konta

    Returns:
        str: Hash MD5 (32 znaki)
    """
    # Tworzymy string z kluczowych danych
    hash_string = (
        f"{account_id}|"
        f"{transaction.transaction_date.isoformat()}|"
        f"{transaction.amount:.2f}|"
        f"{transaction.description}"
        f"{transaction.balance_after:.2f}" if transaction.balance_after is not None else "NULL"
    )

    # Generujemy hash MD5
    return hashlib.md5(hash_string.encode('utf-8')).hexdigest()


def transaction_exists(import_hash: str) -> bool:
    """
    Sprawdza, czy transakcja o danym hash już istnieje w bazie

    Args:
        import_hash: Hash transakcji

    Returns:
        bool: True jeśli istnieje, False jeśli nie
    """
    query = "SELECT COUNT(*) FROM transactions WHERE import_hash = ?"
    results = execute_query(query, (import_hash,))

    count = results[0][0]
    return count > 0


def save_transaction(transaction: Transaction) -> int:
    """
    Zapisuje transakcję do bazy danych

    Args:
        transaction: Obiekt Transaction

    Returns:
        int: ID zapisanej transakcji (lub 0 jeśli duplikat)
    """
    # 1. Pobierz/utwórz konto
    account_id = get_or_create_account(
        platform_name=transaction.platform_name,
        account_name=transaction.account_name,
        currency_code=transaction.currency_code
    )

    # 2. Wygeneruj hash
    import_hash = generate_import_hash(transaction, account_id)

    # 3. Sprawdź, czy transakcja już istnieje
    if transaction_exists(import_hash):
        return 0  # Duplikat - pomijamy

    # 4. Pobierz ID z słowników
    currency_id = get_currency_id(transaction.currency_code)
    transaction_type_id = get_transaction_type_id(transaction.transaction_type)

    # Payment method może być None
    payment_method_id = None
    if transaction.payment_method:
        payment_method_id = get_payment_method_id(transaction.payment_method)

    # Category może być None
    category_id = None
    if transaction.category_name:
        category_id = get_category_id(transaction.category_name)

    # Commission - jeśli None to 0
    commission = transaction.commission or 0

    # 5. Wstaw transakcję do bazy
    query = """
           INSERT INTO transactions (
               account_id, transaction_date, transaction_type_id, payment_method_id,
               amount, commission, currency_id, category_id, description, balance_after,
               notes, source_file, import_hash
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
       """

    params = (
        account_id,
        transaction.transaction_date,
        transaction_type_id,
        payment_method_id,
        transaction.amount,
        commission,
        currency_id,
        category_id,
        transaction.description,
        transaction.balance_after,
        transaction.notes,
        transaction.source_file,
        import_hash
    )

    return execute_insert(query, params)