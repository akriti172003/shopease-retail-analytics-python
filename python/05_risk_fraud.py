import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "output" / "reports"


def load_data():
    file_path = PROCESSED_DATA_DIR / "retail_master.csv"
    return pd.read_csv(file_path)


def detect_risk(master):
    df = master.copy()

    # ---------------------------------------------------------
    # 1. High Transaction Value
    # ---------------------------------------------------------
    q1 = df["net_revenue"].quantile(0.25)
    q3 = df["net_revenue"].quantile(0.75)
    iqr = q3 - q1

    high_value_threshold = q3 + (1.5 * iqr)

    df["high_value_flag"] = (
        df["net_revenue"] > high_value_threshold
    ).astype(int)

    # ---------------------------------------------------------
    # 2. Unusually High Quantity
    # ---------------------------------------------------------
    quantity_threshold = df["quantity"].quantile(0.95)

    df["high_quantity_flag"] = (
        df["quantity"] > quantity_threshold
    ).astype(int)

    # ---------------------------------------------------------
    # 3. Extreme Discount
    # ---------------------------------------------------------
    discount_threshold = df["discount_pct"].quantile(0.95)

    df["extreme_discount_flag"] = (
        df["discount_pct"] >= discount_threshold
    ).astype(int)

    # ---------------------------------------------------------
    # 4. Customer Spending Anomaly
    # ---------------------------------------------------------
    customer_avg = df.groupby("customer_id")["net_revenue"].transform("mean")

    df["customer_spending_anomaly_flag"] = (
        df["net_revenue"] > customer_avg * 2
    ).astype(int)

    # ---------------------------------------------------------
    # 5. Risk Score
    # ---------------------------------------------------------
    df["risk_score"] = (
        df["high_value_flag"] * 30
        + df["high_quantity_flag"] * 20
        + df["extreme_discount_flag"] * 15
        + df["customer_spending_anomaly_flag"] * 35
    )

    # ---------------------------------------------------------
    # 6. Risk Category
    # ---------------------------------------------------------
    df["risk_category"] = np.select(
        [
            df["risk_score"] >= 60,
            df["risk_score"] >= 30
        ],
        [
            "High",
            "Medium"
        ],
        default="Low"
    )

    return df, high_value_threshold, quantity_threshold, discount_threshold


def save_results(df):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "risk_fraud_analysis.csv"

    df.to_csv(output_file, index=False)

    return output_file


def print_summary(
    df,
    high_value_threshold,
    quantity_threshold,
    discount_threshold,
    output_file
):

    total_transactions = len(df)

    high_risk = (df["risk_category"] == "High").sum()
    medium_risk = (df["risk_category"] == "Medium").sum()
    low_risk = (df["risk_category"] == "Low").sum()

    suspicious_transactions = high_risk + medium_risk

    risk_rate = (
        suspicious_transactions / total_transactions * 100
    )

    high_risk_revenue = df.loc[
        df["risk_category"] == "High",
        "net_revenue"
    ].sum()

    print("\n" + "=" * 65)
    print("RETAIL ANALYTICS - RISK & FRAUD DETECTION")
    print("=" * 65)

    print(f"\nTotal transactions       : {total_transactions:,}")
    print(f"Low-risk transactions    : {low_risk:,}")
    print(f"Medium-risk transactions : {medium_risk:,}")
    print(f"High-risk transactions   : {high_risk:,}")
    print(f"Suspicious transactions  : {suspicious_transactions:,}")
    print(f"Risk rate                : {risk_rate:.2f}%")

    print("\nRisk thresholds:")
    print(f"High transaction value   : ₹{high_value_threshold:,.2f}")
    print(f"High quantity threshold  : {quantity_threshold:.0f}")
    print(f"Extreme discount         : {discount_threshold:.0f}%")

    print(f"\nHigh-risk revenue        : ₹{high_risk_revenue:,.2f}")

    print("\nRisk category distribution:")
    print(
        df["risk_category"]
        .value_counts()
        .to_string()
    )

    print("\nTop 10 high-risk transactions:")

    top_risk = df[
        df["risk_category"] == "High"
    ].sort_values(
        "risk_score",
        ascending=False
    )

    print(
        top_risk[
            [
                "order_id",
                "customer_id",
                "net_revenue",
                "quantity",
                "discount_pct",
                "risk_score",
                "risk_category"
            ]
        ].head(10).to_string(index=False)
    )

    print("\nOutput file:")
    print(output_file)

    print("\n" + "=" * 65)
    print("RISK ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 65)


def main():

    master = load_data()

    (
        risk_data,
        high_value_threshold,
        quantity_threshold,
        discount_threshold
    ) = detect_risk(master)

    output_file = save_results(risk_data)

    print_summary(
        risk_data,
        high_value_threshold,
        quantity_threshold,
        discount_threshold,
        output_file
    )


if __name__ == "__main__":
    main()