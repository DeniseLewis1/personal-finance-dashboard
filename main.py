import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from data_validation import run_data_validation
from dashboard import *

def main():
    transactions_df = pd.read_csv("transactions.csv")
    categories_df = pd.read_csv("categories.csv")

    # Explore data files
    #run_data_validation(transactions_df, categories_df)

    # Connect to database
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    # Create tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        account TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT CHECK(type IN ('income', 'expense')) NOT NULL
    );
    """)

    # Insert data into categories table
    categories_df.to_sql("categories", conn, if_exists="replace", index=False)

    categories_df = pd.read_sql("SELECT * FROM categories", conn)
    category_mapping = dict(zip(categories_df['name'], categories_df['id']))

    other_expense_id = category_mapping.get("Other")
    other_income_id = category_mapping.get("Other Income")


    def get_category_id(row):
        category_name = row['category']
        amount = row['amount']
        
        if category_name in category_mapping:
            return category_mapping[category_name]
        
        else:
            return other_income_id if amount > 0 else other_expense_id


    ################################
    # DATA CHECKS HERE
    ################################

    # Insert data into transactions table
    transactions_df['category_id'] = transactions_df.apply(get_category_id, axis=1)
    transactions_df.drop(columns=['category'], inplace=True)
    transactions_df['date'] = pd.to_datetime(transactions_df['date'], format='%m/%d/%y')
    transactions_df.to_sql('transactions', conn, if_exists='replace', index=False)


    # Query transactions
    query = """
        SELECT 
            t.date,
            t.name,
            c.name AS category_name,
            t.amount,
            t.account,
            CASE
                WHEN t.amount > 0 THEN 'income'
                ELSE 'expense'
            END AS type
        FROM transactions t 
        LEFT JOIN categories c 
            ON t.category_id = c.id
    """
    df = pd.read_sql(query, conn)

    # Format date and create month_year column
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.to_period('M')

    print(df)


    # Grouping and aggregation by month
    monthly_aggregated_df = (
        df.groupby(['month_year'])
        .agg(
            income=('amount', lambda x: x[df.loc[x.index, 'type'] == 'income'].sum()),
            expenses=('amount', lambda x: x[df.loc[x.index, 'type'] == 'expense'].sum())
        )
        .reset_index()
    )

    # Add abs_expenses, net_balance, month_year_str, month columns
    monthly_aggregated_df['abs_expenses'] = monthly_aggregated_df['expenses'].abs()
    monthly_aggregated_df['net_balance'] = monthly_aggregated_df['income'] + monthly_aggregated_df['expenses']
    monthly_aggregated_df['month_year_str'] = monthly_aggregated_df['month_year'].astype(str)
    monthly_aggregated_df['month'] = monthly_aggregated_df['month_year'].dt.strftime('%b')

    print(monthly_aggregated_df)


    # Filter data for last two years
    current_year = monthly_aggregated_df['month_year'].dt.year.max()
    last_year = current_year - 1
    current_year_data = monthly_aggregated_df[monthly_aggregated_df['month_year'].dt.year == current_year]
    last_year_data = monthly_aggregated_df[monthly_aggregated_df['month_year'].dt.year == last_year]

    # Sort data by month
    current_year_data = current_year_data.sort_values('month_year')
    last_year_data = last_year_data.sort_values('month_year')
    
    # Calculate totals
    total_income = round(df[df['type'] == 'income']['amount'].sum(), 2)
    total_expenses = round(df[df['type'] == 'expense']['amount'].sum(), 2)
    net_balance = round(total_income + total_expenses, 2)

    # Group by category
    expenses_by_category = (abs(df[df['type'] == 'expense'].groupby('category_name')['amount'].sum()).sort_values(ascending=False))
    income_by_category = (abs(df[df['type'] == 'income'].groupby('category_name')['amount'].sum()).sort_values(ascending=False))

    # Group by month
    expenses_by_month = (abs(df[df['type'] == 'expense'].groupby('month_year')['amount'].sum()))
    income_by_month = (abs(df[df['type'] == 'income'].groupby('month_year')['amount'].sum()))
    net_balance_by_month = round(income_by_month - expenses_by_month, 2)

    print(f"Total Income: ${total_income}")
    print(f"Total Expenses: ${abs(total_expenses)}")
    print(f"Net Balance: ${net_balance}")
    print("\nExpenses by Category:")
    print(expenses_by_category)
    print("\nIncome by Category:")
    print(income_by_category)
    print("\nNet Balance by Month:")
    print(net_balance_by_month)

    # Dashboard
    st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")
    st.title("Personal Finance Dashboard")
    display_metrics(income_by_month, expenses_by_month, net_balance_by_month)
    display_grid(current_year_data, last_year_data, expenses_by_category, current_year, last_year)

    conn.close()

if __name__ == "__main__":
    main()