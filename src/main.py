#!/usr/bin/env python3
"""
Personal Finance Tracker - Main CLI Interface
Handles all user commands and ensures proper data organization.
"""

import os
import sys
import click
from pathlib import Path
from expense_processor import ExpenseProcessor
from budget_analyzer import BudgetAnalyzer
from report_generator import ReportGenerator


class FinanceTracker:
    """Main finance tracker class that coordinates all operations."""
    
    def __init__(self):
        """Initialize the finance tracker and ensure data directory exists."""
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.charts_dir = self.data_dir / "charts"
        self.reports_dir = self.data_dir / "reports"
        
        # Create data directories if they don't exist
        self._ensure_data_directories()
        
        # Initialize components
        self.expense_processor = ExpenseProcessor(self.data_dir)
        self.budget_analyzer = BudgetAnalyzer(self.data_dir)
        self.report_generator = ReportGenerator(self.data_dir)
    
    def _ensure_data_directories(self):
        """Create all necessary data directories."""
        directories = [self.data_dir, self.charts_dir, self.reports_dir]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✓ Ensured directory exists: {directory}")
    
    def demo(self):
        """Generate demo data for testing."""
        print("🎯 Generating demo data...")
        
        # Generate sample expenses
        demo_expenses = [
            {"date": "2024-01-15", "description": "Grocery Store", "amount": 45.67, "category": "Groceries", "payment_method": "Credit Card"},
            {"date": "2024-01-16", "description": "Gas Station", "amount": 35.00, "category": "Transportation", "payment_method": "Cash"},
            {"date": "2024-01-17", "description": "Restaurant", "amount": 28.50, "category": "Dining", "payment_method": "Credit Card"},
            {"date": "2024-01-18", "description": "Netflix Subscription", "amount": 15.99, "category": "Entertainment", "payment_method": "Debit Card"},
            {"date": "2024-01-19", "description": "Electric Bill", "amount": 89.45, "category": "Utilities", "payment_method": "Bank Transfer"},
            {"date": "2024-01-20", "description": "Coffee Shop", "amount": 4.50, "category": "Dining", "payment_method": "Cash"},
            {"date": "2024-01-21", "description": "Movie Theater", "amount": 24.00, "category": "Entertainment", "payment_method": "Credit Card"},
            {"date": "2024-01-22", "description": "Pharmacy", "amount": 12.75, "category": "Healthcare", "payment_method": "Credit Card"},
            {"date": "2024-01-23", "description": "Clothing Store", "amount": 67.89, "category": "Shopping", "payment_method": "Credit Card"},
            {"date": "2024-01-24", "description": "Gym Membership", "amount": 49.99, "category": "Health & Fitness", "payment_method": "Debit Card"}
        ]
        
        # Generate sample budget
        demo_budget = [
            {"category": "Groceries", "monthly_limit": 500.00},
            {"category": "Transportation", "monthly_limit": 200.00},
            {"category": "Dining", "monthly_limit": 300.00},
            {"category": "Entertainment", "monthly_limit": 150.00},
            {"category": "Utilities", "monthly_limit": 250.00},
            {"category": "Healthcare", "monthly_limit": 100.00},
            {"category": "Shopping", "monthly_limit": 200.00},
            {"category": "Health & Fitness", "monthly_limit": 100.00}
        ]
        
        # Save demo data
        self.expense_processor.save_expenses(demo_expenses)
        self.budget_analyzer.save_budget(demo_budget)
        
        print("✅ Demo data generated successfully!")
        print(f"📁 Data saved to: {self.data_dir}")
        print(f"   - Expenses: {self.data_dir}/expenses.csv")
        print(f"   - Budget: {self.data_dir}/budget.csv")
    
    def import_expenses(self, file_path):
        """Import expenses from CSV file."""
        if not os.path.exists(file_path):
            print(f"❌ Error: File '{file_path}' not found.")
            return
        
        print(f"📥 Importing expenses from: {file_path}")
        try:
            imported_count = self.expense_processor.import_from_csv(file_path)
            print(f"✅ Successfully imported {imported_count} expenses!")
        except Exception as e:
            print(f"❌ Error importing expenses: {e}")
    
    def analyze(self):
        """Analyze expenses and generate budget insights."""
        print("📊 Analyzing expenses and budget...")
        
        try:
            # Load and analyze data
            expenses = self.expense_processor.load_expenses()
            budget = self.budget_analyzer.load_budget()
            
            if expenses.empty:
                print("⚠️  No expenses found. Run 'demo' first or import expenses.")
                return
            
            # Perform analysis
            analysis = self.budget_analyzer.analyze_budget(expenses, budget)
            
            # Display results
            print("\n" + "="*50)
            print("📈 BUDGET ANALYSIS RESULTS")
            print("="*50)
            
            print(f"\n💰 Total Expenses: ${analysis['total_spent']:.2f}")
            print(f"📅 Period: {analysis['start_date']} to {analysis['end_date']}")
            print(f"📊 Average Daily Spending: ${analysis['avg_daily']:.2f}")
            
            print("\n📋 Category Breakdown:")
            for category, data in analysis['category_breakdown'].items():
                spent = data['spent']
                limit = data.get('limit', 'No limit')
                remaining = data.get('remaining', 'N/A')
                
                if isinstance(limit, (int, float)):
                    limit_str = f"${limit:.2f}"
                    remaining_str = f"${remaining:.2f}" if isinstance(remaining, (int, float)) else remaining
                    status = "🟢" if remaining >= 0 else "🔴"
                else:
                    limit_str = limit
                    remaining_str = remaining
                    status = "⚪"
                
                print(f"  {status} {category}: ${spent:.2f} / {limit_str} (Remaining: {remaining_str})")
            
            # Show overspend alerts
            if analysis['overspend_alerts']:
                print("\n🚨 OVERSPEND ALERTS:")
                for alert in analysis['overspend_alerts']:
                    print(f"  ⚠️  {alert}")
            
            print("\n✅ Analysis complete!")
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
    
    def report(self):
        """Generate comprehensive financial reports and charts."""
        print("📄 Generating comprehensive financial reports...")
        
        try:
            # Load data
            expenses = self.expense_processor.load_expenses()
            budget = self.budget_analyzer.load_budget()
            
            if expenses.empty:
                print("⚠️  No expenses found. Run 'demo' first or import expenses.")
                return
            
            # Generate reports and charts
            self.report_generator.generate_all_reports(expenses, budget)
            
            print("✅ Reports generated successfully!")
            print(f"📁 Reports saved to: {self.reports_dir}")
            print(f"📊 Charts saved to: {self.charts_dir}")
            
        except Exception as e:
            print(f"❌ Error generating reports: {e}")


# CLI Commands
@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Personal Finance Tracker - Track, analyze, and report on your finances."""
    pass


@cli.command()
def demo():
    """Generate demo data for testing the system."""
    tracker = FinanceTracker()
    tracker.demo()


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def import_expenses(file_path):
    """Import expenses from a CSV file."""
    tracker = FinanceTracker()
    tracker.import_expenses(file_path)


@cli.command()
def analyze():
    """Analyze expenses and generate budget insights."""
    tracker = FinanceTracker()
    tracker.analyze()


@cli.command()
def report():
    """Generate comprehensive financial reports and charts."""
    tracker = FinanceTracker()
    tracker.report()


if __name__ == "__main__":
    cli()
