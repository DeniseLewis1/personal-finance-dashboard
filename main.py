import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from data_validation import run_data_validation

transactions_df = pd.read_csv("transactions.csv")
categories_df = pd.read_csv("categories.csv")

# Explore data files
run_data_validation(transactions_df, categories_df)

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


# Insert data into transactions table
transactions_df['category_id'] = transactions_df.apply(get_category_id, axis=1)
transactions_df.drop(columns=['category'], inplace=True)
transactions_df.to_sql('transactions', conn, if_exists='append', index=False)

conn.close()