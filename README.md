# Personal Finance Tracker CLI

A command-line application for tracking personal finances with data visualization capabilities. Built with Python and Poetry for modern dependency management and build automation.

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 💰 Track income and expenses
- 📊 Categorize transactions automatically
- 📈 Generate financial summaries and reports
- 🎨 Create visualizations (pie charts)
- 💾 Export data to CSV
- 🗄️ SQLite database for data persistence
- 🎯 Beautiful terminal UI with rich formatting

## Prerequisites

- **Python**: 3.9 or higher
- **Poetry**: Latest version (build tool)
- **Operating System**: Linux, macOS, or Windows

### Installing Poetry

```bash
# Linux, macOS, Windows (WSL)
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Verify installation
poetry --version
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/kholoud512/personal-finance-tracker.git
cd personal-finance-tracker
```

### 2. Install Dependencies

Poetry will automatically handle all dependencies:

```bash
# Install all dependencies (production + development)
poetry install

# Install only production dependencies
poetry install --no-dev
```

This command will:
- Create a virtual environment
- Install all required packages (click, rich, peewee, pandas, matplotlib)
- Set up the CLI command `finance`

## Building the Project

### Create Distributable Package

```bash
# Build wheel and sdist packages
poetry build
```

This creates:
- `dist/personal_finance_tracker-0.1.0-py3-none-any.whl` (wheel package)
- `dist/personal-finance-tracker-0.1.0.tar.gz` (source distribution)

### Version Management

Update version in `pyproject.toml`:

```bash
# Bump patch version (0.1.0 -> 0.1.1)
poetry version patch

# Bump minor version (0.1.0 -> 0.2.0)
poetry version minor

# Bump major version (0.1.0 -> 1.0.0)
poetry version major
```

## Usage

### Activate Virtual Environment

```bash
# Enter poetry shell
poetry shell

# Now you can use the 'finance' command directly
```

Or run commands without activating shell:

```bash
poetry run finance --help
```

### Available Commands

#### Add a Transaction

```bash
# Add an expense
finance add -a 50.00 -d "Grocery shopping" -c food -t expense

# Add income
finance add -a 2000.00 -d "Monthly salary" -c salary -t income

# Add with specific date
finance add -a 30.00 -d "Bus pass" -c transport -t expense --date 2024-11-01
```

#### List Transactions

```bash
# List last 10 transactions
finance list

# List last 20 transactions
finance list --limit 20

# Filter by type
finance list --type income
finance list --type expense
```

#### View Summary

```bash
# Current month summary
finance summary

# Specific month
finance summary --month 10 --year 2024
```

#### Generate Chart

```bash
# Generate chart for current month
finance chart

# Specific month with custom output
finance chart --month 10 --year 2024 --output october_expenses.png
```

#### Delete Transaction

```bash
# Delete by ID (get ID from 'finance list')
finance delete 5
```

#### Export Data

```bash
# Export all transactions to CSV
finance export

# Custom filename
finance export --output my_finances.csv
```

## Project Structure

```
personal-finance-tracker/
├── finance_tracker/           # Main package directory
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # CLI interface and commands
│   ├── database.py           # Database models (Peewee ORM)
│   └── reports.py            # Reports and visualization
├── tests/                    # Test directory (for Lecture 5)
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_cli.py
│   └── test_reports.py
├── dist/                     # Built packages (created by 'poetry build')
├── pyproject.toml           # Poetry configuration and dependencies
├── poetry.lock              # Lock file with exact versions
├── README.md                # This file
└── .gitignore              # Git ignore rules
```

## Dependencies

### Production Dependencies

- **click** (^8.1.7): CLI framework for building command-line interfaces
- **rich** (^13.7.0): Beautiful terminal formatting and tables
- **peewee** (^3.17.0): Lightweight ORM for SQLite database
- **pandas** (^2.1.4): Data manipulation and CSV export
- **matplotlib** (^3.8.2): Data visualization (charts)
- **python-dateutil** (^2.8.2): Date parsing utilities

### Development Dependencies

- **pytest** (^7.4.3): Testing framework
- **pytest-cov** (^4.1.0): Test coverage reporting
- **black** (^23.12.1): Code formatter
- **ruff** (^0.1.9): Fast Python linter

## Build Automation Features

### 1. Dependency Management
All dependencies are declared in `pyproject.toml` with version constraints. Poetry resolves and locks exact versions in `poetry.lock`.

```bash
# Add new dependency
poetry add requests

# Add development dependency
poetry add --group dev pytest

# Update dependencies
poetry update
```

### 2. Virtual Environment
Poetry automatically creates and manages isolated virtual environments:

```bash
# Show environment info
poetry env info

# List environments
poetry env list
```

### 3. Packaging
Build distributable packages:

```bash
# Create wheel and source distribution
poetry build

# Publish to PyPI (when ready)
poetry publish
```

### 4. Scripts
CLI entry point is defined in `pyproject.toml`:

```toml
[tool.poetry.scripts]
finance = "finance_tracker.cli:main"
```

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=finance_tracker

# Run specific test file
poetry run pytest tests/test_cli.py
```

## Code Quality

```bash
# Format code with black
poetry run black finance_tracker/

# Lint code with ruff
poetry run ruff check finance_tracker/

# Fix linting issues automatically
poetry run ruff check --fix finance_tracker/
```

## Database

The application uses SQLite database stored at:
- **Linux/Mac**: `~/.finance_tracker.db`
- **Windows**: `C:\Users\kholoud512\.finance_tracker.db`

Database schema:
- **categories**: id, name, created_at
- **transactions**: id, amount, description, category_id, transaction_type, date, created_at

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Format code: `poetry run black .`
5. Run tests: `poetry run pytest`
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Poetry not found
```bash
# Add Poetry to PATH (Linux/Mac)
export PATH="$HOME/.local/bin:$PATH"

# Windows: Add to PATH manually or reinstall
```

### Module not found error
```bash
# Ensure dependencies are installed
poetry install

# Activate shell
poetry shell
```

### Database permission error
```bash
# Check database location
ls -la ~/.finance_tracker.db

# If needed, delete and reinitialize
rm ~/.finance_tracker.db
finance list  # Will recreate database
```

## Author

**Kholoud Ibrahim**
Email: thmanabrahym512@gmail.com
Another Email: kholoudibrahim512@gmail.com
GitHub: [@kholoud512](https://github.com/kholoud512)

## Acknowledgments

- Built with [Poetry](https://python-poetry.org/) for dependency management
- CLI powered by [Click](https://click.palletsprojects.com/)
- Beautiful output with [Rich](https://rich.readthedocs.io/)
- Database with [Peewee ORM](http://docs.peewee-orm.com/)

---

**Build Tool Demonstration**: Poetry for Python project management
