import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

df = pd.read_csv("transactions.csv")

conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

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

conn.close()