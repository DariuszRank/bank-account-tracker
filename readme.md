# Finance Tracker

Personal finance tracking and analysis application with support for multiple banks and currencies. Built with Python and SQLite, featuring automated transaction import, duplicate detection, and modular architecture designed for scalability.

## Overview

Finance Tracker is a Python-based application designed to consolidate financial data from multiple banking institutions into a single SQLite database. The application implements a complete ETL (Extract, Transform, Load) pipeline with bank-specific CSV parsers, transaction normalization, and comprehensive financial analysis capabilities.

## Key Features

- **Multi-Bank Support**: Modular parser architecture supporting different CSV formats from various banks
- **Automated Import**: ETL pipeline with automatic data extraction, transformation, and loading
- **Duplicate Detection**: Hash-based transaction deduplication preventing data redundancy
- **Commission Tracking**: Native support for bank fees and commissions linked to transactions
- **Multi-Currency**: Support for multiple currencies (PLN, EUR, USD, CHF, GBP, NOK, BGN)
- **Data Integrity**: Foreign key constraints, database indexes, and transaction validation
- **Extensible Design**: Clean architecture allowing easy addition of new banks and features

## Technology Stack

- **Language**: Python 3.12
- **Database**: SQLite 3
- **Libraries**: 
  - `csv` - CSV file parsing
  - `dataclasses` - Data modeling
  - `hashlib` - Transaction hashing
  - `sqlite3` - Database operations
  - `python-dateutil` - Date parsing

## Supported Banks

| Bank | Status | Features |
|------|--------|----------|
| Citibank | ✅ Active | Basic transactions, balance tracking |
| Credit Agricole | ✅ Active | Transactions with commissions, balance tracking |

## Project Architecture

### Design Principles

- **Separation of Concerns**: Clear separation between data access, business logic, and parsing
- **Single Responsibility**: Each module handles one specific aspect of the application
- **DRY (Don't Repeat Yourself)**: Reusable components and base classes
- **Modular Design**: Easy to extend with new banks, payment methods, or categories

### Data Flow

    CSV File → Parser → Transaction Model → Import Service → Database

### Directory Structure

    bank_account_tracker/
    ├── db/                         # Database layer
    │   ├── create_database.py      # Schema definition and initialization
    │   ├── connection.py           # Connection management
    │   └── repositories.py         # Data access layer (CRUD operations)
    │
    ├── models/                     # Data models
    │   └── transaction.py          # Transaction dataclass model
    │
    ├── parsers/                    # Bank-specific CSV parsers
    │   ├── base_parser.py          # Abstract parser interface
    │   ├── citibank_parser.py      # Citibank CSV parser
    │   └── credit_agricole_parser.py  # Credit Agricole CSV parser
    │
    ├── services/                   # Business logic
    │   └── import_service.py       # Import orchestration and statistics
    │
    ├── data/                       # Data directory
    │   └── imports/                # CSV files location
    │
    ├── config.py                   # Configuration management
    └── main.py                     # Application entry point

## Database Schema

### Core Tables

- **platforms**: Banking institutions
- **accounts**: User accounts across different platforms
- **transactions**: Financial transactions with commission support
- **currencies**: Supported currency definitions
- **transaction_types**: Transaction type taxonomy (Income, Expense, Transfer, etc.)
- **payment_methods**: Payment method classification
- **categories**: User-defined transaction categories

### Key Features

- Foreign key constraints enabled
- Indexed columns for query optimization (date, account, category, hash)
- Unique constraint on import hash for duplicate prevention
- Commission field for bank fee tracking

## Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Setup

1. Clone the repository:

        git clone https://github.com/your-username/finance-tracker.git
        cd finance-tracker

2. Create and activate virtual environment:

        python -m venv .venv
        .venv\Scripts\Activate.ps1  # Windows PowerShell
        source .venv/bin/activate   # macOS/Linux

3. Install dependencies:

        pip install -r requirements.txt

4. Initialize database:

        python -m db.create_database

## Usage


### Transaction Model

    @dataclass
    class Transaction:
        transaction_date: date
        amount: float
        description: str
        platform_name: str
        account_name: str
        currency_code: str
        transaction_type: str
        payment_method: Optional[str]
        category_name: Optional[str]
        balance_after: Optional[float]
        commission: Optional[float]  # Bank fees/commissions
        notes: Optional[str]
        source_file: Optional[str]

## Implementation Highlights

### 1. Duplicate Detection

Transaction uniqueness is determined by MD5 hash of:
- Account ID
- Transaction date
- Amount
- Description

This approach ensures the same CSV can be imported multiple times without creating duplicates.

### 2. Commission Handling

Bank fees and commissions are stored in a separate field allowing:
- Accurate total impact calculation (`amount + commission`)
- Separate analysis of bank fees
- Preservation of original transaction amounts

### 3. Encoding Support

Parsers support multiple encodings:
- UTF-8 with BOM (Citibank)
- Windows-1250 (Credit Agricole - Polish characters)

### 4. Flexible Date Parsing

Support for various date formats:
- DD/MM/YYYY (Citibank)
- DD.MM.YYYY (Credit Agricole)
- Extensible for additional formats

## Development Roadmap

### Planned Features

- [ ] Automatic transaction categorization using rules engine
- [ ] Transfer detection between own accounts
- [ ] Budget tracking and alerts
- [ ] Web interface (Flask/Django)
- [ ] Data visualization (charts, graphs)
- [ ] Export to Excel/PDF
- [ ] Additional bank parsers

### Future Enhancements

- [ ] REST API for external integrations
- [ ] Machine learning-based categorization

## Project Status

🚧 **Active Development** - Core functionality complete, analytics module in progress

## Technical Decisions

### Why SQLite?

- Zero configuration
- Serverless architecture
- Perfect for single-user applications
- Easy backup (single file)
- ACID compliance

### Why Dataclasses?

- Clean, readable code
- Type hints support
- Built-in methods (`__init__`, `__repr__`)
- No external dependencies

### Why Modular Parsers?

- Each bank has unique CSV format
- Easy to add new banks
- Isolated testing
- Maintainable codebase

## Contributing

This is a personal project, but suggestions and feedback are welcome. Feel free to open an issue for discussion.

## License

This project is private and for personal use.

## Contact

For questions or opportunities, please reach out via GitHub.

