# Personal Finance Tracker

A comprehensive Python-based personal finance tracking system with expense categorization, budget analysis, and automated reporting.

## Features

- **Expense Tracking**: Import and track personal expenses with CSV support
- **Auto-Categorization**: Intelligent categorization of expenses
- **Budget Analysis**: Set budgets and get overspend alerts
- **Chart Generation**: Generate pie, bar, and line charts for visual analysis
- **CLI Interface**: Easy-to-use command-line interface
- **Data Persistence**: All data automatically saved and persisted between sessions

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd finance-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start Workflow

1. **Generate demo data**:
```bash
python src/main.py demo
```

2. **Analyze expenses and budgets**:
```bash
python src/main.py analyze
```

3. **Generate comprehensive reports**:
```bash
python src/main.py report
```

### Available Commands

- `demo`: Generate sample expense and budget data
- `import <file>`: Import expenses from CSV file
- `analyze`: Analyze expenses and generate budget insights
- `report`: Generate comprehensive financial reports and charts
- `help`: Show available commands

### Data Organization

All generated files are automatically organized in the `data/` directory:
- `data/expenses.csv`: Expense records
- `data/budget.csv`: Budget categories and limits
- `data/charts/`: Generated visualization charts
- `data/reports/`: Financial reports in PDF format

## Project Structure

```
finance-tracker/
├── src/
│   ├── main.py              # Main CLI interface
│   ├── expense_processor.py # Expense processing and categorization
│   ├── budget_analyzer.py   # Budget analysis and alerts
│   └── report_generator.py  # Report and chart generation
├── data/                    # Auto-created data directory
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Data Format

### Expenses CSV Format
```csv
date,description,amount,category,payment_method
2024-01-15,Grocery Store,45.67,Groceries,Credit Card
2024-01-16,Gas Station,35.00,Transportation,Cash
```

### Budget CSV Format
```csv
category,monthly_limit,current_spent,remaining
Groceries,500.00,245.67,254.33
Transportation,200.00,135.00,65.00
```

## License

MIT License
