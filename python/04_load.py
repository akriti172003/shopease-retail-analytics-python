# ============================================================
# RETAIL ANALYTICS ETL PIPELINE
# Step 4: LOAD
# ============================================================

import pandas as pd
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Raw data directory
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

# Processed data directory
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"


def load_raw_data():
    """Load raw datasets."""

    orders = pd.read_csv(RAW_DATA_DIR / "orders.csv")
    products = pd.read_csv(RAW_DATA_DIR / "products.csv")
    customers = pd.read_csv(RAW_DATA_DIR / "customers.csv")

    return orders, products, customers


def transform_data(orders, products, customers):
    """Create the final analytical master table."""

    orders = orders.copy()
    products = products.copy()
    customers = customers.copy()

    # -----------------------------
    # Date transformations
    # -----------------------------

    orders["order_date"] = pd.to_datetime(
        orders["order_date"],
        errors="coerce"
    )

    orders["year"] = orders["order_date"].dt.year
    orders["month"] = orders["order_date"].dt.month
    orders["month_name"] = orders["order_date"].dt.strftime("%b")
    orders["day_name"] = orders["order_date"].dt.day_name()
    orders["quarter"] = orders["order_date"].dt.quarter

    # -----------------------------
    # Customer transformations
    # -----------------------------

    customers["join_date"] = pd.to_datetime(
        customers["join_date"],
        errors="coerce"
    )

    analysis_date = pd.Timestamp("2024-12-31")

    customers["tenure_days"] = (
        analysis_date - customers["join_date"]
    ).dt.days

    customers["tenure_years"] = (
        customers["tenure_days"] / 365
    ).round(1)

    conditions = [
        customers["age"] < 25,
        customers["age"] < 35,
        customers["age"] < 45
    ]

    choices = [
        "18-24",
        "25-34",
        "35-44"
    ]

    import numpy as np

    customers["age_group"] = np.select(
        conditions,
        choices,
        default="45+"
    )

    # -----------------------------
    # Merge datasets
    # -----------------------------

    master = orders.merge(
        products,
        on="product_id",
        how="inner"
    )

    master = master.merge(
        customers[
            [
                "customer_id",
                "age",
                "gender",
                "city",
                "age_group",
                "tenure_years"
            ]
        ],
        on="customer_id",
        how="inner"
    )

    # -----------------------------
    # Business metrics
    # -----------------------------

    master["gross_revenue"] = (
        master["quantity"] *
        master["unit_price"]
    )

    master["discount_amt"] = (
        master["gross_revenue"] *
        master["discount_pct"] / 100
    )

    master["net_revenue"] = (
        master["gross_revenue"] -
        master["discount_amt"]
    )

    master["cost"] = (
        master["quantity"] *
        master["unit_cost"]
    )

    master["profit"] = (
        master["net_revenue"] -
        master["cost"]
    )

    master["profit_margin"] = (
        master["profit"] /
        master["net_revenue"] *
        100
    ).round(2)

    # -----------------------------
    # Discount buckets
    # -----------------------------

    bins = [-1, 0, 5, 10, 15, 20]

    labels = [
        "No Discount",
        "5%",
        "10%",
        "15%",
        "20%"
    ]

    master["discount_bucket"] = pd.cut(
        master["discount_pct"],
        bins=bins,
        labels=labels
    )

    return master


def save_processed_data(master):
    """Save final analytical dataset."""

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        PROCESSED_DATA_DIR /
        "retail_master.csv"
    )

    master.to_csv(
        output_file,
        index=False
    )

    return output_file


def main():

    print("=" * 60)
    print("RETAIL ANALYTICS ETL PIPELINE")
    print("STEP 4: LOAD")
    print("=" * 60)

    # Extract
    orders, products, customers = load_raw_data()

    # Transform
    master = transform_data(
        orders,
        products,
        customers
    )

    # Load
    output_file = save_processed_data(master)

    print("\nETL LOAD COMPLETED")
    print("-" * 60)
    print(f"Rows loaded    : {len(master):,}")
    print(f"Columns loaded : {len(master.columns)}")
    print(f"Output file    : {output_file}")

    print("\nFinal dataset preview:")
    print(master.head())

    print("\n" + "=" * 60)
    print("ETL PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()