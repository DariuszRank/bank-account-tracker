"""
Moduł zarządzający połączeniami z bazą danych
"""

import sqlite3
from config import DATABASE_PATH


def get_connection():
    """
    Zwraca połączenie z bazą danych SQLite

    Returns:
        sqlite3.Connection: Połączenie z bazą danych
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Umożliwia dostęp do kolumn po nazwach
    conn.execute("PRAGMA foreign_keys = ON;")  # Włącza klucze obce
    return conn


def execute_query(query, params=None):
    """
    Wykonuje zapytanie SELECT i zwraca wyniki

    Args:
        query (str): Zapytanie SQL
        params (tuple): Parametry zapytania (opcjonalne)

    Returns:
        list: Lista wyników
    """
    conn = get_connection()
    cursor = conn.cursor()

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    results = cursor.fetchall()
    conn.close()

    return results


def execute_insert(query, params=None):
    """
    Wykonuje zapytanie INSERT/UPDATE/DELETE i zwraca ID ostatniego rekordu

    Args:
        query (str): Zapytanie SQL
        params (tuple): Parametry zapytania (opcjonalne)

    Returns:
        int: ID ostatnio wstawionego rekordu (dla INSERT)
    """
    conn = get_connection()
    cursor = conn.cursor()

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    last_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return last_id


def execute_many(query, params_list):
    """
    Wykonuje wiele zapytań INSERT jednocześnie (batch insert)

    Args:
        query (str): Zapytanie SQL
        params_list (list): Lista krotek z parametrami

    Returns:
        int: Liczba wstawionych rekordów
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany(query, params_list)

    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    return rows_affected