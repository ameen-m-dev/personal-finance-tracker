"""
Report Generator - Creates charts and PDF reports for financial analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from fpdf import FPDF
import os

# Set matplotlib style for better-looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class ReportGenerator:
    """Generates charts and PDF reports for financial analysis."""
    
    def __init__(self, data_dir: Path):
        """Initialize the report generator with data directory."""
        self.data_dir = data_dir
        self.charts_dir = data_dir / "charts"
        self.reports_dir = data_dir / "reports"
        
        # Ensure directories exist
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all_reports(self, expenses: pd.DataFrame, budget: pd.DataFrame) -> None:
        """Generate all charts and reports."""
        print("📊 Generating charts...")
        self.generate_expense_pie_chart(expenses)
        self.generate_category_bar_chart(expenses)
        self.generate_spending_timeline(expenses)
        self.generate_budget_vs_actual(expenses, budget)
        
        print("📄 Generating PDF report...")
        self.generate_pdf_report(expenses, budget)
        
        print("✅ All reports generated successfully!")
    
    def generate_expense_pie_chart(self, expenses: pd.DataFrame) -> None:
        """Generate pie chart of expenses by category."""
        if expenses.empty:
            print("⚠️  No expenses data available for pie chart.")
            return
        
        # Group by category and sum amounts
        category_totals = expenses.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        # Create pie chart
        plt.figure(figsize=(12, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_totals)))
        
        wedges, texts, autotexts = plt.pie(
            category_totals.values,
            labels=category_totals.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 10}
        )
        
        # Enhance text appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.title('Expense Distribution by Category', fontsize=16, fontweight='bold', pad=20)
        plt.axis('equal')
        
        # Add total amount as text
        total_amount = category_totals.sum()
        plt.figtext(0.5, 0.02, f'Total Expenses: ${total_amount:,.2f}', 
                   ha='center', fontsize=12, fontweight='bold')
        
        # Save chart
        chart_path = self.charts_dir / "expense_pie_chart.png"
        plt.tight_layout()
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Pie chart saved: {chart_path}")
    
    def generate_category_bar_chart(self, expenses: pd.DataFrame) -> None:
        """Generate bar chart of expenses by category."""
        if expenses.empty:
            print("⚠️  No expenses data available for bar chart.")
            return
        
        # Group by category and sum amounts
        category_totals = expenses.groupby('category')['amount'].sum().sort_values(ascending=True)
        
        # Create bar chart
        plt.figure(figsize=(12, 8))
        colors = plt.cm.viridis(np.linspace(0, 1, len(category_totals)))
        
        bars = plt.barh(category_totals.index, category_totals.values, color=colors)
        
        # Add value labels on bars
        for bar, value in zip(bars, category_totals.values):
            plt.text(bar.get_width() + max(category_totals.values) * 0.01, 
                    bar.get_y() + bar.get_height()/2, 
                    f'${value:,.2f}', 
                    va='center', fontweight='bold')
        
        plt.title('Expenses by Category', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Amount ($)', fontsize=12)
        plt.ylabel('Category', fontsize=12)
        plt.grid(axis='x', alpha=0.3)
        
        # Save chart
        chart_path = self.charts_dir / "category_bar_chart.png"
        plt.tight_layout()
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Bar chart saved: {chart_path}")
    
    def generate_spending_timeline(self, expenses: pd.DataFrame) -> None:
        """Generate line chart of spending over time."""
        if expenses.empty:
            print("⚠️  No expenses data available for timeline chart.")
            return
        
        # Group by date and sum amounts
        daily_spending = expenses.groupby('date')['amount'].sum().reset_index()
        daily_spending = daily_spending.sort_values('date')
        
        # Create line chart
        plt.figure(figsize=(14, 8))
        
        plt.plot(daily_spending['date'], daily_spending['amount'], 
                marker='o', linewidth=2, markersize=6, color='#2E86AB')
        
        # Add trend line
        z = np.polyfit(range(len(daily_spending)), daily_spending['amount'], 1)
        p = np.poly1d(z)
        plt.plot(daily_spending['date'], p(range(len(daily_spending))), 
                "--", alpha=0.8, color='red', label='Trend')
        
        plt.title('Daily Spending Timeline', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Amount ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Save chart
        chart_path = self.charts_dir / "spending_timeline.png"
        plt.tight_layout()
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Timeline chart saved: {chart_path}")
    
    def generate_budget_vs_actual(self, expenses: pd.DataFrame, budget: pd.DataFrame) -> None:
        """Generate comparison chart of budget vs actual spending."""
        if expenses.empty or budget.empty:
            print("⚠️  Insufficient data for budget vs actual chart.")
            return
        
        # Calculate actual spending by category
        actual_spending = expenses.groupby('category')['amount'].sum()
        
        # Create comparison data
        comparison_data = []
        categories = []
        
        for _, budget_row in budget.iterrows():
            category = budget_row['category']
            budget_amount = budget_row['monthly_limit']
            actual_amount = actual_spending.get(category, 0)
            
            categories.append(category)
            comparison_data.append({
                'Budget': budget_amount,
                'Actual': actual_amount
            })
        
        if not comparison_data:
            print("⚠️  No matching categories between budget and expenses.")
            return
        
        # Create comparison chart
        df_comparison = pd.DataFrame(comparison_data, index=categories)
        
        plt.figure(figsize=(14, 8))
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = plt.bar(x - width/2, df_comparison['Budget'], width, 
                       label='Budget', color='#2E86AB', alpha=0.8)
        bars2 = plt.bar(x + width/2, df_comparison['Actual'], width, 
                       label='Actual', color='#A23B72', alpha=0.8)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + max(df_comparison.max()) * 0.01,
                        f'${height:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.title('Budget vs Actual Spending by Category', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Category', fontsize=12)
        plt.ylabel('Amount ($)', fontsize=12)
        plt.xticks(x, categories, rotation=45)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        # Save chart
        chart_path = self.charts_dir / "budget_vs_actual.png"
        plt.tight_layout()
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Budget comparison chart saved: {chart_path}")
    
    def generate_pdf_report(self, expenses: pd.DataFrame, budget: pd.DataFrame) -> None:
        """Generate comprehensive PDF financial report."""
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 20, 'Personal Finance Report', ln=True, align='C')
        pdf.ln(10)
        
        # Report date
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', ln=True)
        pdf.ln(10)
        
        # Executive Summary
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 15, 'Executive Summary', ln=True)
        pdf.set_font('Arial', '', 12)
        
        if not expenses.empty:
            total_spent = expenses['amount'].sum()
            total_transactions = len(expenses)
            avg_transaction = expenses['amount'].mean()
            start_date = expenses['date'].min().strftime('%B %d, %Y')
            end_date = expenses['date'].max().strftime('%B %d, %Y')
            
            pdf.cell(0, 10, f'Total Expenses: ${total_spent:,.2f}', ln=True)
            pdf.cell(0, 10, f'Total Transactions: {total_transactions}', ln=True)
            pdf.cell(0, 10, f'Average Transaction: ${avg_transaction:.2f}', ln=True)
            pdf.cell(0, 10, f'Period: {start_date} to {end_date}', ln=True)
        else:
            pdf.cell(0, 10, 'No expense data available.', ln=True)
        
        pdf.ln(10)
        
        # Top Categories
        if not expenses.empty:
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 15, 'Top Spending Categories', ln=True)
            pdf.set_font('Arial', '', 12)
            
            category_totals = expenses.groupby('category')['amount'].sum().sort_values(ascending=False)
            for i, (category, amount) in enumerate(category_totals.head(5).items(), 1):
                percentage = (amount / category_totals.sum()) * 100
                pdf.cell(0, 10, f'{i}. {category}: ${amount:,.2f} ({percentage:.1f}%)', ln=True)
        
        pdf.ln(10)
        
        # Budget Analysis
        if not budget.empty:
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 15, 'Budget Analysis', ln=True)
            pdf.set_font('Arial', '', 12)
            
            total_budget = budget['monthly_limit'].sum()
            total_spent_budget = budget['current_spent'].sum()
            budget_utilization = (total_spent_budget / total_budget * 100) if total_budget > 0 else 0
            
            pdf.cell(0, 10, f'Total Budget: ${total_budget:,.2f}', ln=True)
            pdf.cell(0, 10, f'Total Spent: ${total_spent_budget:,.2f}', ln=True)
            pdf.cell(0, 10, f'Budget Utilization: {budget_utilization:.1f}%', ln=True)
            
            # Budget alerts
            overspend_categories = budget[budget['remaining'] < 0]
            if not overspend_categories.empty:
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Overspend Alerts:', ln=True)
                pdf.set_font('Arial', '', 12)
                for _, row in overspend_categories.iterrows():
                    overspend_amount = abs(row['remaining'])
                    pdf.cell(0, 10, f'- {row["category"]}: ${overspend_amount:.2f} over budget', ln=True)
        
        pdf.ln(10)
        
        # Charts included
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 15, 'Charts Generated', ln=True)
        pdf.set_font('Arial', '', 12)
        
        chart_files = [
            'expense_pie_chart.png',
            'category_bar_chart.png', 
            'spending_timeline.png',
            'budget_vs_actual.png'
        ]
        
        for chart_file in chart_files:
            chart_path = self.charts_dir / chart_file
            if chart_path.exists():
                pdf.cell(0, 10, f'- {chart_file.replace("_", " ").replace(".png", "").title()}', ln=True)
        
        # Save PDF
        report_path = self.reports_dir / f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(str(report_path))
        
        print(f"📄 PDF report saved: {report_path}")
    
    def get_chart_summary(self) -> Dict[str, Any]:
        """Get summary of generated charts."""
        chart_files = list(self.charts_dir.glob("*.png"))
        
        return {
            'total_charts': len(chart_files),
            'chart_files': [f.name for f in chart_files],
            'charts_dir': str(self.charts_dir),
            'reports_dir': str(self.reports_dir)
        }
