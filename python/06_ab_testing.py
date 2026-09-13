import pandas as pd
from pathlib import Path
from scipy import stats


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "output" / "reports"


def load_data():
    file_path = PROCESSED_DATA_DIR / "retail_master.csv"
    return pd.read_csv(file_path)


def run_ab_test(df):
    # Use 10% discount as Control
    # Use 20% discount as Treatment
    control = df[df["discount_pct"] == 10].copy()
    treatment = df[df["discount_pct"] == 20].copy()

    print("\n" + "=" * 65)
    print("RETAIL ANALYTICS - A/B TESTING")
    print("=" * 65)

    print("\nExperiment design:")
    print("Control   : 10% discount")
    print("Treatment : 20% discount")

    print("\nSample sizes:")
    print(f"Control transactions   : {len(control):,}")
    print(f"Treatment transactions : {len(treatment):,}")

    # ---------------------------------------------------------
    # Business Metrics
    # ---------------------------------------------------------

    control_revenue = control["net_revenue"].mean()
    treatment_revenue = treatment["net_revenue"].mean()

    control_profit = control["profit"].mean()
    treatment_profit = treatment["profit"].mean()

    control_margin = control["profit_margin"].mean()
    treatment_margin = treatment["profit_margin"].mean()

    control_quantity = control["quantity"].mean()
    treatment_quantity = treatment["quantity"].mean()

    # ---------------------------------------------------------
    # Statistical Test
    # ---------------------------------------------------------

    revenue_test = stats.ttest_ind(
        control["net_revenue"],
        treatment["net_revenue"],
        equal_var=False
    )

    profit_test = stats.ttest_ind(
        control["profit"],
        treatment["profit"],
        equal_var=False
    )

    # ---------------------------------------------------------
    # Effect Sizes
    # ---------------------------------------------------------

    revenue_change = (
        (treatment_revenue - control_revenue)
        / control_revenue
        * 100
    )

    profit_change = (
        (treatment_profit - control_profit)
        / control_profit
        * 100
    )

    margin_change = treatment_margin - control_margin

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    print("\nAverage business metrics:")
    print("-" * 65)

    print(f"Average revenue - Control   : ₹{control_revenue:,.2f}")
    print(f"Average revenue - Treatment : ₹{treatment_revenue:,.2f}")
    print(f"Revenue change               : {revenue_change:.2f}%")

    print(f"\nAverage profit - Control    : ₹{control_profit:,.2f}")
    print(f"Average profit - Treatment  : ₹{treatment_profit:,.2f}")
    print(f"Profit change                : {profit_change:.2f}%")

    print(f"\nAverage margin - Control    : {control_margin:.2f}%")
    print(f"Average margin - Treatment  : {treatment_margin:.2f}%")
    print(f"Margin change                : {margin_change:.2f} percentage points")

    print(f"\nAverage quantity - Control  : {control_quantity:.2f}")
    print(f"Average quantity - Treatment: {treatment_quantity:.2f}")

    # ---------------------------------------------------------
    # Statistical Results
    # ---------------------------------------------------------

    print("\nStatistical test - Revenue:")
    print(f"t-statistic : {revenue_test.statistic:.4f}")
    print(f"p-value     : {revenue_test.pvalue:.6f}")

    print("\nStatistical test - Profit:")
    print(f"t-statistic : {profit_test.statistic:.4f}")
    print(f"p-value     : {profit_test.pvalue:.6f}")

    # ---------------------------------------------------------
    # Decision
    # ---------------------------------------------------------

    print("\nBusiness interpretation:")
    print("-" * 65)

    if revenue_test.pvalue < 0.05:
        print("Revenue difference is statistically significant.")
    else:
        print("Revenue difference is NOT statistically significant.")

    if profit_test.pvalue < 0.05:
        print("Profit difference is statistically significant.")
    else:
        print("Profit difference is NOT statistically significant.")

    if treatment_profit > control_profit:
        print("Treatment generates higher average profit.")
    else:
        print("Control generates higher average profit.")

    if treatment_margin > control_margin:
        print("Treatment has a higher average profit margin.")
    else:
        print("Control has a higher average profit margin.")

    print("\nImportant limitation:")
    print(
        "This is an observational comparison of historical discount groups, "
        "not a randomized production A/B experiment."
    )

    print("\n" + "=" * 65)
    print("A/B TEST COMPLETED SUCCESSFULLY")
    print("=" * 65)

    # ---------------------------------------------------------
    # Save summary
    # ---------------------------------------------------------

    results = pd.DataFrame({
        "metric": [
            "Average Revenue",
            "Average Profit",
            "Average Profit Margin",
            "Average Quantity"
        ],
        "control_10pct": [
            control_revenue,
            control_profit,
            control_margin,
            control_quantity
        ],
        "treatment_20pct": [
            treatment_revenue,
            treatment_profit,
            treatment_margin,
            treatment_quantity
        ]
    })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "ab_testing_results.csv"
    results.to_csv(output_file, index=False)

    print(f"\nResults saved to:")
    print(output_file)


def main():
    df = load_data()
    run_ab_test(df)


if __name__ == "__main__":
    main()