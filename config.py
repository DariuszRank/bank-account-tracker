"""
Konfiguracja aplikacji
"""

import os

# Ścieżki
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'finance.db')
DATA_DIR = os.path.join(BASE_DIR, 'data', 'imports')

# Ustawienia bazy danych
DB_NAME = 'finance.db'

# Opcje parsowania
DATE_FORMATS = [
    '%Y-%m-%d',
    '%d.%m.%Y',
    '%d/%m/%Y',
    '%Y/%m/%d'
]