# ============================================================
# RETAIL ANALYTICS ETL PIPELINE
# Step 3: TRANSFORMATION
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Raw data directory
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


def load_data():
    """Load validated raw datasets."""

    orders = pd.read_csv(RAW_DATA_DIR / "orders.csv")
    products = pd.read_csv(RAW_DATA_DIR / "products.csv")
    customers = pd.read_csv(RAW_DATA_DIR / "customers.csv")

    return orders, products, customers


def transform_orders(orders):
    """Transform order-level data."""

    orders = orders.copy()

    # Convert order date
    orders["order_date"] = pd.to_datetime(
        orders["order_date"],
        errors="coerce"
    )

    # Time features
    orders["year"] = orders["order_date"].dt.year
    orders["month"] = orders["order_date"].dt.month
    orders["month_name"] = orders["order_date"].dt.strftime("%b")
    orders["day_name"] = orders["order_date"].dt.day_name()
    orders["quarter"] = orders["order_date"].dt.quarter

    return orders


def transform_customers(customers):
    """Create customer-level features."""

    customers = customers.copy()

    # Convert join date
    customers["join_date"] = pd.to_datetime(
        customers["join_date"],
        errors="coerce"
    )

    # Analysis date
    analysis_date = pd.Timestamp("2024-12-31")

    # Customer tenure
    customers["tenure_days"] = (
        analysis_date - customers["join_date"]
    ).dt.days

    customers["tenure_years"] = (
        customers["tenure_days"] / 365
    ).round(1)

    # Age groups
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

    customers["age_group"] = np.select(
        conditions,
        choices,
        default="45+"
    )

    return customers


def create_master_table(orders, products, customers):
    """Merge orders, products and customers."""

    master = orders.merge(
        products,
        how="inner",
        on="product_id"
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
        how="inner",
        on="customer_id"
    )

    return master


def calculate_business_metrics(master):
    """Calculate revenue, cost and profitability metrics."""

    master = master.copy()

    # Gross revenue
    master["gross_revenue"] = (
        master["quantity"] *
        master["unit_price"]
    )

    # Discount amount
    master["discount_amt"] = (
        master["gross_revenue"] *
        master["discount_pct"] / 100
    )

    # Net revenue
    master["net_revenue"] = (
        master["gross_revenue"] -
        master["discount_amt"]
    )

    # Cost
    master["cost"] = (
        master["quantity"] *
        master["unit_cost"]
    )

    # Profit
    master["profit"] = (
        master["net_revenue"] -
        master["cost"]
    )

    # Profit margin
    master["profit_margin"] = np.where(
        master["net_revenue"] != 0,
        (
            master["profit"] /
            master["net_revenue"]
        ) * 100,
        0
    )

    master["profit_margin"] = (
        master["profit_margin"].round(2)
    )

    return master


def create_discount_buckets(master):
    """Group discounts into business-friendly categories."""

    master = master.copy()

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


def transform_data():

    orders, products, customers = load_data()

    print("=" * 60)
    print("RETAIL ANALYTICS ETL PIPELINE")
    print("STEP 3: TRANSFORMATION")
    print("=" * 60)

    # Transform individual datasets
    orders = transform_orders(orders)
    customers = transform_customers(customers)

    # Merge datasets
    master = create_master_table(
        orders,
        products,
        customers
    )

    print(f"\nMaster table created: {master.shape}")

    # Business metrics
    master = calculate_business_metrics(master)

    # Discount buckets
    master = create_discount_buckets(master)

    print("\nTransformation completed.")

    print("\nNew analytical columns:")
    print([
        "year",
        "month",
        "quarter",
        "age_group",
        "tenure_years",
        "gross_revenue",
        "discount_amt",
        "net_revenue",
        "cost",
        "profit",
        "profit_margin",
        "discount_bucket"
    ])

    print("\nSample transformed data:")
    print(
        master[
            [
                "order_id",
                "order_date",
                "quantity",
                "discount_pct",
                "net_revenue",
                "profit",
                "profit_margin"
            ]
        ].head()
    )

    return master


if __name__ == "__main__":
    master = transform_data()