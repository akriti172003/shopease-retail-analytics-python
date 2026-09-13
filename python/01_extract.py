# ============================================================
# RETAIL ANALYTICS ETL PIPELINE
# Step 1: EXTRACT
# ============================================================

import pandas as pd
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Raw data directory
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


def extract_data():
    """
    Extract raw retail datasets from CSV files.
    """

    orders = pd.read_csv(RAW_DATA_DIR / "orders.csv")
    products = pd.read_csv(RAW_DATA_DIR / "products.csv")
    customers = pd.read_csv(RAW_DATA_DIR / "customers.csv")

    print("=" * 60)
    print("RETAIL ANALYTICS ETL PIPELINE - EXTRACT")
    print("=" * 60)

    print(f"Orders loaded    : {orders.shape}")
    print(f"Products loaded  : {products.shape}")
    print(f"Customers loaded : {customers.shape}")

    print("\nOrders columns:")
    print(list(orders.columns))

    print("\nProducts columns:")
    print(list(products.columns))

    print("\nCustomers columns:")
    print(list(customers.columns))

    return orders, products, customers


if __name__ == "__main__":
    orders, products, customers = extract_data()
    