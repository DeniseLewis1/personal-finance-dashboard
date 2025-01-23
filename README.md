# Personal Finance Dashboard
A dashboard to track income, expenses, and financial trends

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Visuals](#visuals)
7. [Future enhancements](#future-enhancements)

## Introduction
The Personal Finance Dashboard is designed to help users analyze their income, expenses, and financial habits. It provides insights through charts and metrics to support better financial decision-making.

Click [here](https://personal-finance-dashboard-dl.streamlit.app/) to view the dashboard.

## Features
- Display average monthly income, expenses, and net balance
- Data visualizations comparing last two years of income and expenses
- Track monthly net balance over time
- Visualize spending by category

## Technologies Used
- **Backend**: Python, SQLite, ETL
- **Frontend**: Streamlit
- **Data Manipulation**: Pandas
- **Visualization**: Plotly

## Installation
1. Clone the repository:
    ```
    git clone https://github.com/your-username/personal-finance-dashboard.git
    cd personal-finance-dashboard
    ```
2. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Run the application:
    ```
    streamlit run main.py
    ```

## Usage
Replace the `transactions.csv` file with your transactions to personalize the analysis. Enusre the file contains the same columns. The `categories.csv` file can also be modified for custom categories. Launch the application and navigate through the dashboard to view key financial metrics and visualizations.

## Visuals
Dashboard:

![Dashboard](/images/dashboard.png)

Schema:

![Schema](/images/schema.png)

Flow Chart:

![Flow Chart](/images/flow-chart.png)

## Future enhancements
- Integration with real-time financial APIs (e.g., stock data, bank transactions).
- More customizable and interactive charts/metrics.
- Ability to view transactions in a separate tab.