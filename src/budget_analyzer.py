"""
Budget Analyzer - Handles budget management and analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any


class BudgetAnalyzer:
    """Handles budget analysis, tracking, and overspend alerts."""
    
    def __init__(self, data_dir: Path):
        """Initialize the budget analyzer with data directory."""
        self.data_dir = data_dir
        self.budget_file = data_dir / "budget.csv"
    
    def save_budget(self, budget_data: List[Dict[str, Any]]) -> None:
        """Save budget data to CSV file."""
        df = pd.DataFrame(budget_data)
        
        # Ensure we have the required columns
        if 'monthly_limit' in df.columns:
            df['monthly_limit'] = pd.to_numeric(df['monthly_limit'], errors='coerce')
        
        # Initialize current_spent and remaining columns
        if 'current_spent' not in df.columns:
            df['current_spent'] = 0.0
        if 'remaining' not in df.columns:
            df['remaining'] = df['monthly_limit']
        
        # Save to CSV
        df.to_csv(self.budget_file, index=False)
        print(f"💾 Saved budget data to {self.budget_file}")
    
    def load_budget(self) -> pd.DataFrame:
        """Load budget data from CSV file."""
        if not self.budget_file.exists():
            print(f"📝 No existing budget file found. Creating new one at {self.budget_file}")
            return pd.DataFrame(columns=['category', 'monthly_limit', 'current_spent', 'remaining'])
        
        try:
            df = pd.read_csv(self.budget_file)
            # Ensure numeric columns
            numeric_columns = ['monthly_limit', 'current_spent', 'remaining']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            return df
        except Exception as e:
            print(f"❌ Error loading budget: {e}")
            return pd.DataFrame(columns=['category', 'monthly_limit', 'current_spent', 'remaining'])
    
    def update_budget_spending(self, expenses: pd.DataFrame) -> None:
        """Update budget with current spending from expenses."""
        if expenses.empty:
            return
        
        budget_df = self.load_budget()
        if budget_df.empty:
            return
        
        # Calculate current month's spending by category
        current_month = datetime.now().replace(day=1)
        current_month_expenses = expenses[expenses['date'] >= current_month]
        
        if not current_month_expenses.empty:
            category_spending = current_month_expenses.groupby('category')['amount'].sum()
            
            # Update budget with current spending
            for category, spent in category_spending.items():
                if category in budget_df['category'].values:
                    budget_df.loc[budget_df['category'] == category, 'current_spent'] = spent
                    budget_df.loc[budget_df['category'] == category, 'remaining'] = \
                        budget_df.loc[budget_df['category'] == category, 'monthly_limit'] - spent
        
        # Save updated budget
        budget_df.to_csv(self.budget_file, index=False)
    
    def analyze_budget(self, expenses: pd.DataFrame, budget: pd.DataFrame) -> Dict[str, Any]:
        """Analyze budget performance and generate insights."""
        if expenses.empty:
            return {
                'total_spent': 0,
                'start_date': None,
                'end_date': None,
                'avg_daily': 0,
                'category_breakdown': {},
                'overspend_alerts': []
            }
        
        # Update budget with current spending
        self.update_budget_spending(expenses)
        budget = self.load_budget()  # Reload updated budget
        
        # Basic statistics
        total_spent = expenses['amount'].sum()
        start_date = expenses['date'].min().strftime('%Y-%m-%d')
        end_date = expenses['date'].max().strftime('%Y-%m-%d')
        
        # Calculate average daily spending
        date_range = (expenses['date'].max() - expenses['date'].min()).days + 1
        avg_daily = total_spent / date_range if date_range > 0 else 0
        
        # Category breakdown
        category_breakdown = {}
        category_spending = expenses.groupby('category')['amount'].sum()
        
        for category, spent in category_spending.items():
            budget_row = budget[budget['category'] == category]
            
            if not budget_row.empty:
                limit = budget_row.iloc[0]['monthly_limit']
                remaining = budget_row.iloc[0]['remaining']
                category_breakdown[category] = {
                    'spent': spent,
                    'limit': limit,
                    'remaining': remaining,
                    'percentage_used': (spent / limit * 100) if limit > 0 else 0
                }
            else:
                category_breakdown[category] = {
                    'spent': spent,
                    'limit': 'No limit',
                    'remaining': 'N/A',
                    'percentage_used': 0
                }
        
        # Generate overspend alerts
        overspend_alerts = []
        for category, data in category_breakdown.items():
            if isinstance(data['limit'], (int, float)) and data['limit'] > 0:
                if data['spent'] > data['limit']:
                    overspend_amount = data['spent'] - data['limit']
                    overspend_alerts.append(
                        f"{category}: Overspent by ${overspend_amount:.2f} "
                        f"({data['percentage_used']:.1f}% of budget)"
                    )
                elif data['percentage_used'] > 80:
                    overspend_alerts.append(
                        f"{category}: Approaching budget limit "
                        f"({data['percentage_used']:.1f}% used)"
                    )
        
        return {
            'total_spent': total_spent,
            'start_date': start_date,
            'end_date': end_date,
            'avg_daily': avg_daily,
            'category_breakdown': category_breakdown,
            'overspend_alerts': overspend_alerts
        }
    
    def get_budget_summary(self) -> Dict[str, Any]:
        """Get summary of budget performance."""
        budget_df = self.load_budget()
        
        if budget_df.empty:
            return {
                'total_budget': 0,
                'total_spent': 0,
                'total_remaining': 0,
                'budget_utilization': 0,
                'categories_with_budgets': 0
            }
        
        total_budget = budget_df['monthly_limit'].sum()
        total_spent = budget_df['current_spent'].sum()
        total_remaining = budget_df['remaining'].sum()
        budget_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        return {
            'total_budget': total_budget,
            'total_spent': total_spent,
            'total_remaining': total_remaining,
            'budget_utilization': budget_utilization,
            'categories_with_budgets': len(budget_df)
        }
    
    def add_budget_category(self, category: str, monthly_limit: float) -> None:
        """Add a new budget category."""
        budget_df = self.load_budget()
        
        # Check if category already exists
        if category in budget_df['category'].values:
            print(f"⚠️  Category '{category}' already exists in budget.")
            return
        
        new_category = {
            'category': category,
            'monthly_limit': monthly_limit,
            'current_spent': 0.0,
            'remaining': monthly_limit
        }
        
        new_df = pd.DataFrame([new_category])
        combined_df = pd.concat([budget_df, new_df], ignore_index=True)
        
        combined_df.to_csv(self.budget_file, index=False)
        print(f"✅ Added budget category: {category} - ${monthly_limit:.2f}/month")
    
    def update_budget_limit(self, category: str, new_limit: float) -> None:
        """Update budget limit for a category."""
        budget_df = self.load_budget()
        
        if category not in budget_df['category'].values:
            print(f"❌ Category '{category}' not found in budget.")
            return
        
        # Update the limit and recalculate remaining
        budget_df.loc[budget_df['category'] == category, 'monthly_limit'] = new_limit
        budget_df.loc[budget_df['category'] == category, 'remaining'] = \
            new_limit - budget_df.loc[budget_df['category'] == category, 'current_spent']
        
        budget_df.to_csv(self.budget_file, index=False)
        print(f"✅ Updated budget limit for {category}: ${new_limit:.2f}/month")
    
    def get_spending_trends(self, expenses: pd.DataFrame, days: int = 30) -> Dict[str, Any]:
        """Analyze spending trends over time."""
        if expenses.empty:
            return {
                'daily_spending': [],
                'weekly_spending': [],
                'trend_direction': 'stable',
                'peak_spending_day': None
            }
        
        # Filter for recent data
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_expenses = expenses[expenses['date'] >= cutoff_date].copy()
        
        if recent_expenses.empty:
            return {
                'daily_spending': [],
                'weekly_spending': [],
                'trend_direction': 'stable',
                'peak_spending_day': None
            }
        
        # Daily spending
        daily_spending = recent_expenses.groupby('date')['amount'].sum().reset_index()
        daily_spending = daily_spending.sort_values('date')
        
        # Weekly spending
        recent_expenses['week'] = recent_expenses['date'].dt.isocalendar().week
        weekly_spending = recent_expenses.groupby('week')['amount'].sum().reset_index()
        
        # Determine trend direction
        if len(daily_spending) > 1:
            first_half = daily_spending.iloc[:len(daily_spending)//2]['amount'].mean()
            second_half = daily_spending.iloc[len(daily_spending)//2:]['amount'].mean()
            
            if second_half > first_half * 1.1:
                trend_direction = 'increasing'
            elif second_half < first_half * 0.9:
                trend_direction = 'decreasing'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'stable'
        
        # Find peak spending day
        peak_day = daily_spending.loc[daily_spending['amount'].idxmax()]
        peak_spending_day = {
            'date': peak_day['date'].strftime('%Y-%m-%d'),
            'amount': peak_day['amount']
        }
        
        return {
            'daily_spending': daily_spending.to_dict('records'),
            'weekly_spending': weekly_spending.to_dict('records'),
            'trend_direction': trend_direction,
            'peak_spending_day': peak_spending_day
        }
