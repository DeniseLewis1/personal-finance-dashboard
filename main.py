import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from data_validation import run_data_validation

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
#transactions_df.to_sql('transactions', conn, if_exists='append', index=False)


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


# Filter data for 2023 and 2024
data_last_year = monthly_aggregated_df[monthly_aggregated_df['month_year'].dt.year == 2023]
data_current_year = monthly_aggregated_df[monthly_aggregated_df['month_year'].dt.year == 2024]


# Sort data by month
data_last_year = data_last_year.sort_values('month_year')
data_current_year = data_current_year.sort_values('month_year')


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

# Streamlit
st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")
st.title("Personal Finance Dashboard")

# Display metrics in three columns
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div style="padding: 10px; margin-bottom: 30px; border: 1px solid #ccc; background-color: #f4f4f4; text-align: center;">
            <strong>Avg. Monthly Income</strong><br>
            <span style="font-size: 24px; font-weight: bold">${income_by_month.mean():,.2f}</span>
        </div>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown(f"""
        <div style="padding: 10px; margin-bottom: 30px; border: 1px solid #ccc; background-color: #f4f4f4; text-align: center;">
            <strong>Avg. Monthly Expenses</strong><br>
            <span style="font-size: 24px; font-weight: bold">${expenses_by_month.mean():,.2f}</span>
        </div>
    """, unsafe_allow_html=True)
    
with col3:
    st.markdown(f"""
        <div style="padding: 10px; margin-bottom: 30px; border: 1px solid #ccc; background-color: #f4f4f4; text-align: center;">
            <strong>Avg. Monthly Net Balance</strong><br>
            <span style="font-size: 24px; font-weight: bold">${net_balance_by_month.mean():,.2f}</span>
        </div>
    """, unsafe_allow_html=True)


# Create a 2x2 grid layout
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

chart_width = 600
chart_height = 325
font_size = max(10, min(chart_width // 40, 30))

# First chart in top-left corner
with col1:
    # Create a bar chart for 2024 income
    bar_chart1 = go.Bar(
        x=data_current_year['month'],
        y=data_current_year['income'],
        name="2024",
        marker=dict(color='#4CAF50'),
        hovertemplate="$%{y:,.2f}<extra>2024</extra>"
    )

    # Create a line chart for 2023 income
    line_chart1 = go.Scatter(
        x=data_last_year['month'],
        y=data_last_year['income'],
        mode='lines+markers',
        name="2023",
        line=dict(color='#333333', width=2, dash='dash'),
        marker=dict(size=6),
        hovertemplate="$%{y:,.2f}<extra>2023</extra>"
    )

    # Combine charts into one figure
    fig1 = go.Figure()
    fig1.add_trace(bar_chart1)
    fig1.add_trace(line_chart1)

    # Update layout
    fig1.update_layout(
        width=chart_width,
        height=chart_height,
        margin=dict(l=10, r=10, t=50, b=20),
        title=dict(
            text="Income",
            font=dict(size=font_size),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=None,
            tickmode='array',
            tickvals=data_last_year['month'],
            ticktext=data_last_year['month'],
        ),
        yaxis=dict(
            title=None,
            tickformat="$~s"
        ),
        legend=dict(title="Year"),
        barmode='overlay',
        paper_bgcolor="#f4f4f4",
        plot_bgcolor="#f4f4f4"
    )
    st.plotly_chart(fig1)

# Second chart in top-right corner
with col2:
    # Create a bar chart for 2024 expenses
    bar_chart2 = go.Bar(
        x=data_current_year['month'],
        y=data_current_year['abs_expenses'],
        name="2024",
        marker=dict(color='#FF5733'),
        hovertemplate="$%{y:,.2f}<extra>2024</extra>"
    )

    # Create a line chart for 2023 expenses
    line_chart2 = go.Scatter(
        x=data_last_year['month'],
        y=data_last_year['abs_expenses'],
        mode='lines+markers',
        name="2023",
        line=dict(color='#333333', width=2, dash='dash'),
        marker=dict(size=6),
        hovertemplate="$%{y:,.2f}<extra>2023</extra>"
    )

    # Combine charts into one figure
    fig2 = go.Figure()
    fig2.add_trace(bar_chart2)
    fig2.add_trace(line_chart2)

    # Update layout
    fig2.update_layout(
        width=chart_width,
        height=chart_height,
        margin=dict(l=10, r=10, t=50, b=20),
        title=dict(
            text="Expenses",
            font=dict(size=font_size),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=None,
            tickmode='array',
            tickvals=data_last_year['month'],
            ticktext=data_last_year['month'],
        ),
        yaxis=dict(
            title=None,
            tickformat="$~s"
        ),
        legend=dict(title="Year"),
        barmode='overlay',
        paper_bgcolor="#f4f4f4",
        plot_bgcolor="#f4f4f4"
    )
    st.plotly_chart(fig2)

# Third chart in bottom-left corner
with col3:
    fig3 = px.line(data_current_year, x='month', y='net_balance')
    fig3.update_layout(
        width=chart_width,
        height=chart_height,
        margin=dict(l=10, r=10, t=50, b=20),
        xaxis_title=None, 
        yaxis_title=None, 
        xaxis=dict(tickmode='array',
            tickvals=data_current_year['month'],
            ticktext=data_current_year['month'],
        ),
        yaxis=dict(tickformat="$~s"),
        title=dict(text="Net Balance", font=dict(size=font_size), x=0.5, xanchor='center'),
        paper_bgcolor="#f4f4f4",
        plot_bgcolor="#f4f4f4"
    )
    fig3.update_traces(
        hovertemplate="$%{y:,.2f}<extra></extra>",
        fill="tozeroy",
    )
    st.plotly_chart(fig3)

# Fourth chart in bottom-right corner
with col4:
    fig4 = px.pie(expenses_by_category, values=expenses_by_category, names=expenses_by_category.index)
    fig4.update_layout(
        width=chart_width,
        height=chart_height,
        margin=dict(l=10, r=10, t=50, b=20),
        title=dict(text="Spending by Category", font=dict(size=font_size), x=0.5, xanchor='center'),
        paper_bgcolor="#f4f4f4",
        plot_bgcolor="#f4f4f4"
    )
    fig4.update_traces(
        hovertemplate="%{label}: $%{value:,.2f}<extra></extra>"
    )
    st.plotly_chart(fig4)

conn.close()