import pandas as pd

def explore_data(transactions_df, categories_df):
    print("Transactions DataFrame:\n")
    print(transactions_df.head(), "\n")
    print(transactions_df.info(), "\n")
    print("Shape:", transactions_df.shape, "\n")
    print(transactions_df.describe(), "\n")
    print("Duplicated Rows:\n", transactions_df[transactions_df.duplicated()], "\n")
    print("Rows with NULL values:\n", transactions_df[transactions_df.isnull().any(axis=1)], "\n")
    print("Rows with NA values:\n", transactions_df[transactions_df.isna().any(axis=1)], "\n")

    print("Categories DataFrame:\n")
    print(categories_df.head(), "\n")
    print(categories_df.info(), "\n")
    print("Shape:", categories_df.shape, "\n")
    print("Duplicated Rows:\n", categories_df[categories_df.duplicated()], "\n")
    print("Rows with NULL values:\n", categories_df[categories_df.isnull().any(axis=1)], "\n")
    print("Rows with NA values:\n", categories_df[categories_df.isna().any(axis=1)], "\n")

def validate_categories(df):
    # Check for expected columns
    expected_columns = ["id", "name", "type"]
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing column(s): {', '.join(missing_columns)}")

    # Check for duplicates
    df["type"] = df["type"].str.lower()
    columns_to_check = ["id"]
    df = df.drop_duplicates(subset=columns_to_check, keep="first")
    columns_to_check = ["name", "type"]
    df = df.drop_duplicates(subset=columns_to_check, keep="first")

    # Check for NULLS and NAs
    if df.isnull().values.any() or df.isna().values.any():
        raise ValueError("Data contains NULL (NaN) value(s).")

    # Check for invalid ids
    if df["id"].dtype != "int64":
        raise ValueError(f"Invalid id(s) found, ids must be an integer.")

    # Check for invalid transaction types
    valid_types = ["income", "expense"]
    invalid_types = df[~df["type"].isin(valid_types)]
    if not invalid_types.empty:
        raise ValueError(f"Invalid type(s) found: {', '.join(invalid_types["type"].unique())}")

def validate_transactions(df):
    # Check for expected columns
    expected_columns = ["date", "name", "category", "amount", "account"]
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing column(s): {', '.join(missing_columns)}")
    
    # Check for duplicates
    df = df.drop_duplicates(keep="first")

    # Check for NULLS and NAs
    if df.isnull().values.any() or df.isna().values.any():
        raise ValueError("Data contains NULL (NaN) value(s).")

    # Check for invalid dates
    try:
        df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y")
    except:
            raise ValueError(f"Invalid date, date must be in mm/dd/yy format.")

    # Check for invalid amounts
    if df["amount"].dtype != "float64":
       raise ValueError(f"Invalid amount(s) found, amounts must be a float.")