"""
Expense Processor - Handles expense data management and categorization.
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class ExpenseProcessor:
    """Handles expense data processing, categorization, and CSV operations."""
    
    def __init__(self, data_dir: Path):
        """Initialize the expense processor with data directory."""
        self.data_dir = data_dir
        self.expenses_file = data_dir / "expenses.csv"
        
        # Define categorization rules
        self.category_keywords = {
            'Groceries': ['grocery', 'supermarket', 'food', 'market', 'fresh', 'organic'],
            'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'parking', 'metro', 'bus'],
            'Dining': ['restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'dining', 'food court'],
            'Entertainment': ['movie', 'theater', 'netflix', 'spotify', 'amazon prime', 'concert'],
            'Utilities': ['electric', 'water', 'gas bill', 'internet', 'phone', 'utility'],
            'Healthcare': ['pharmacy', 'doctor', 'medical', 'dental', 'health', 'clinic'],
            'Shopping': ['clothing', 'store', 'mall', 'amazon', 'target', 'walmart', 'shopping'],
            'Health & Fitness': ['gym', 'fitness', 'yoga', 'workout', 'sports', 'athletic'],
            'Education': ['book', 'course', 'class', 'tuition', 'education', 'learning'],
            'Travel': ['hotel', 'flight', 'airline', 'vacation', 'travel', 'trip']
        }
    
    def save_expenses(self, expenses: List[Dict[str, Any]]) -> None:
        """Save expenses to CSV file."""
        df = pd.DataFrame(expenses)
        
        # Ensure date column is properly formatted
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # Auto-categorize expenses if category is missing
        if 'category' in df.columns:
            df['category'] = df.apply(
                lambda row: self._auto_categorize(row['description']) 
                if pd.isna(row['category']) or row['category'] == '' 
                else row['category'], 
                axis=1
            )
        
        # Save to CSV
        df.to_csv(self.expenses_file, index=False)
        print(f"💾 Saved {len(expenses)} expenses to {self.expenses_file}")
    
    def load_expenses(self) -> pd.DataFrame:
        """Load expenses from CSV file."""
        if not self.expenses_file.exists():
            print(f"📝 No existing expenses file found. Creating new one at {self.expenses_file}")
            return pd.DataFrame(columns=['date', 'description', 'amount', 'category', 'payment_method'])
        
        try:
            df = pd.read_csv(self.expenses_file)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            print(f"❌ Error loading expenses: {e}")
            return pd.DataFrame(columns=['date', 'description', 'amount', 'category', 'payment_method'])
    
    def import_from_csv(self, file_path: str) -> int:
        """Import expenses from external CSV file."""
        try:
            # Read the external CSV
            df = pd.read_csv(file_path)
            
            # Validate required columns
            required_columns = ['date', 'description', 'amount']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Standardize column names
            column_mapping = {
                'Date': 'date',
                'Description': 'description', 
                'Amount': 'amount',
                'Category': 'category',
                'Payment Method': 'payment_method',
                'Payment_Method': 'payment_method'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Ensure we have the required columns
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Add category and payment_method if missing
            if 'category' not in df.columns:
                df['category'] = ''
            if 'payment_method' not in df.columns:
                df['payment_method'] = 'Unknown'
            
            # Auto-categorize expenses
            df['category'] = df.apply(
                lambda row: self._auto_categorize(row['description']) 
                if pd.isna(row['category']) or row['category'] == '' 
                else row['category'], 
                axis=1
            )
            
            # Convert date format
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            
            # Convert amount to numeric
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            # Remove rows with invalid amounts
            df = df.dropna(subset=['amount'])
            
            # Load existing expenses
            existing_df = self.load_expenses()
            
            # Combine with existing data
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            
            # Remove duplicates based on date, description, and amount
            combined_df = combined_df.drop_duplicates(subset=['date', 'description', 'amount'])
            
            # Save combined data
            combined_df.to_csv(self.expenses_file, index=False)
            
            return len(df)
            
        except Exception as e:
            raise Exception(f"Error importing CSV: {e}")
    
    def _auto_categorize(self, description: str) -> str:
        """Auto-categorize expense based on description."""
        if pd.isna(description) or description == '':
            return 'Uncategorized'
        
        description_lower = description.lower()
        
        # Check each category's keywords
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category
        
        # Check for common patterns
        patterns = {
            r'\b(restaurant|cafe|coffee|pizza|burger|dining)\b': 'Dining',
            r'\b(gas|fuel|uber|lyft|taxi|parking)\b': 'Transportation',
            r'\b(grocery|supermarket|food|market)\b': 'Groceries',
            r'\b(movie|theater|netflix|spotify|concert)\b': 'Entertainment',
            r'\b(electric|water|gas bill|internet|phone)\b': 'Utilities',
            r'\b(pharmacy|doctor|medical|dental|clinic)\b': 'Healthcare',
            r'\b(clothing|store|mall|amazon|target|walmart)\b': 'Shopping',
            r'\b(gym|fitness|yoga|workout|sports)\b': 'Health & Fitness'
        }
        
        for pattern, category in patterns.items():
            if re.search(pattern, description_lower):
                return category
        
        return 'Uncategorized'
    
    def get_expense_summary(self) -> Dict[str, Any]:
        """Get summary statistics of expenses."""
        df = self.load_expenses()
        
        if df.empty:
            return {
                'total_expenses': 0,
                'total_transactions': 0,
                'avg_transaction': 0,
                'date_range': None,
                'top_categories': []
            }
        
        summary = {
            'total_expenses': df['amount'].sum(),
            'total_transactions': len(df),
            'avg_transaction': df['amount'].mean(),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d'),
                'end': df['date'].max().strftime('%Y-%m-%d')
            },
            'top_categories': df.groupby('category')['amount'].sum().sort_values(ascending=False).head(5).to_dict()
        }
        
        return summary
    
    def add_expense(self, date: str, description: str, amount: float, 
                   category: str = '', payment_method: str = 'Unknown') -> None:
        """Add a single expense."""
        if not category:
            category = self._auto_categorize(description)
        
        expense = {
            'date': date,
            'description': description,
            'amount': amount,
            'category': category,
            'payment_method': payment_method
        }
        
        # Load existing expenses
        df = self.load_expenses()
        
        # Add new expense
        new_df = pd.DataFrame([expense])
        combined_df = pd.concat([df, new_df], ignore_index=True)
        
        # Save
        combined_df.to_csv(self.expenses_file, index=False)
        print(f"✅ Added expense: {description} - ${amount:.2f} ({category})")
