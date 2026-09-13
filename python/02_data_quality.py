# ============================================================
# RETAIL ANALYTICS ETL PIPELINE
# Step 2: DATA QUALITY & VALIDATION
# ============================================================

import pandas as pd
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Raw data directory
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


def load_data():
    """Load raw datasets for quality checks."""

    orders = pd.read_csv(RAW_DATA_DIR / "orders.csv")
    products = pd.read_csv(RAW_DATA_DIR / "products.csv")
    customers = pd.read_csv(RAW_DATA_DIR / "customers.csv")

    return orders, products, customers


def check_missing_values(df, table_name):
    """Check missing values in a dataset."""

    missing = df.isnull().sum()

    print(f"\n--- Missing Values: {table_name} ---")

    if missing.sum() == 0:
        print("PASS - No missing values found.")
    else:
        print(missing[missing > 0])


def check_duplicates(df, table_name):
    """Check duplicate rows."""

    duplicates = df.duplicated().sum()

    print(f"\n--- Duplicate Rows: {table_name} ---")

    if duplicates == 0:
        print("PASS - No duplicate rows found.")
    else:
        print(f"WARNING - {duplicates} duplicate rows found.")


def check_orders(orders):
    """Validate order-level business rules."""

    print("\n" + "=" * 60)
    print("ORDER VALIDATION")
    print("=" * 60)

    # Quantity validation
    invalid_quantity = (orders["quantity"] <= 0).sum()

    if invalid_quantity == 0:
        print("PASS - All quantities are greater than zero.")
    else:
        print(f"FAIL - {invalid_quantity} orders have invalid quantities.")

    # Discount validation
    invalid_discount = (
        (orders["discount_pct"] < 0) |
        (orders["discount_pct"] > 100)
    ).sum()

    if invalid_discount == 0:
        print("PASS - All discounts are between 0% and 100%.")
    else:
        print(f"FAIL - {invalid_discount} orders have invalid discounts.")

    # Date validation
    dates = pd.to_datetime(orders["order_date"], errors="coerce")
    invalid_dates = dates.isna().sum()

    if invalid_dates == 0:
        print("PASS - All order dates are valid.")
    else:
        print(f"FAIL - {invalid_dates} invalid order dates found.")


def check_referential_integrity(orders, products, customers):
    """Check whether order IDs reference valid products and customers."""

    print("\n" + "=" * 60)
    print("REFERENTIAL INTEGRITY")
    print("=" * 60)

    invalid_products = (
        ~orders["product_id"].isin(products["product_id"])
    ).sum()

    invalid_customers = (
        ~orders["customer_id"].isin(customers["customer_id"])
    ).sum()

    if invalid_products == 0:
        print("PASS - All product IDs exist in products table.")
    else:
        print(
            f"FAIL - {invalid_products} orders contain invalid product IDs."
        )

    if invalid_customers == 0:
        print("PASS - All customer IDs exist in customers table.")
    else:
        print(
            f"FAIL - {invalid_customers} orders contain invalid customer IDs."
        )


def run_quality_checks():

    orders, products, customers = load_data()

    print("=" * 60)
    print("RETAIL ANALYTICS ETL PIPELINE")
    print("STEP 2: DATA QUALITY & VALIDATION")
    print("=" * 60)

    # Missing-value checks
    check_missing_values(orders, "Orders")
    check_missing_values(products, "Products")
    check_missing_values(customers, "Customers")

    # Duplicate checks
    check_duplicates(orders, "Orders")
    check_duplicates(products, "Products")
    check_duplicates(customers, "Customers")

    # Business-rule checks
    check_orders(orders)

    # Relationship checks
    check_referential_integrity(
        orders,
        products,
        customers
    )

    print("\n" + "=" * 60)
    print("DATA QUALITY CHECKS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run_quality_checks()