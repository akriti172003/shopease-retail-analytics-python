import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "output" / "reports"


def load_data():
    file_path = PROCESSED_DATA_DIR / "retail_master.csv"
    return pd.read_csv(file_path)


def generate_business_insights(df):

    total_revenue = df["net_revenue"].sum()
    total_profit = df["profit"].sum()
    profit_margin = (total_profit / total_revenue) * 100

    total_orders = len(df)
    average_order_value = df["net_revenue"].mean()

    # Category analysis
    category_revenue = (
        df.groupby("category")["net_revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    best_category = category_revenue.index[0]

    # Discount analysis
    discount_analysis = (
        df.groupby("discount_pct")
        .agg(
            orders=("order_id", "count"),
            revenue=("net_revenue", "sum"),
            profit=("profit", "sum"),
            margin=("profit_margin", "mean")
        )
        .reset_index()
    )

    # Highest and lowest profit discount groups
    best_discount = discount_analysis.loc[
        discount_analysis["profit"].idxmax()
    ]

    worst_discount = discount_analysis.loc[
        discount_analysis["profit"].idxmin()
    ]

    # Risk analysis
    high_value_threshold = (
        df["net_revenue"].quantile(0.75)
        + 1.5 *
        (
            df["net_revenue"].quantile(0.75)
            - df["net_revenue"].quantile(0.25)
        )
    )

    high_value_transactions = (
        df["net_revenue"] > high_value_threshold
    ).sum()

    # ---------------------------------------------------------
    # Generate natural-language business insights
    # ---------------------------------------------------------

    insights = []

    insights.append(
        f"Overall, the business generated ₹{total_revenue:,.2f} "
        f"in net revenue from {total_orders:,} transactions, "
        f"with total profit of ₹{total_profit:,.2f} "
        f"and an overall profit margin of {profit_margin:.2f}%."
    )

    insights.append(
        f"The {best_category} category generated the highest "
        f"total revenue among all product categories."
    )

    insights.append(
        f"The discount level associated with the highest total "
        f"profit was {int(best_discount['discount_pct'])}%, "
        f"generating approximately ₹{best_discount['profit']:,.2f} "
        f"in profit."
    )

    insights.append(
        f"The {int(worst_discount['discount_pct'])}% discount group "
        f"generated approximately ₹{worst_discount['profit']:,.2f} "
        f"in profit, making it the lowest-profit discount group."
    )

    insights.append(
        f"{high_value_transactions:,} transactions exceeded the "
        f"statistical high-value threshold of "
        f"₹{high_value_threshold:,.2f} and may require additional "
        f"transaction-level review."
    )

    # ---------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------

    recommendations = []

    if best_discount["discount_pct"] < worst_discount["discount_pct"]:
        recommendations.append(
            "Prioritize lower discount levels where possible, "
            "as higher discounts are associated with weaker "
            "profitability in the historical dataset."
        )

    recommendations.append(
        "Review unusually high-value transactions using the "
        "risk-scoring framework before approving exceptional "
        "orders or promotions."
    )

    recommendations.append(
        f"Focus growth initiatives on the {best_category} category "
        "while monitoring whether additional sales volume translates "
        "into incremental profit."
    )

    # ---------------------------------------------------------
    # AI-ready prompt
    # ---------------------------------------------------------

    ai_prompt = f"""
You are a senior retail business analyst.

Analyze the following verified business metrics and provide
concise, evidence-based business recommendations.

Total orders: {total_orders:,}
Total revenue: ₹{total_revenue:,.2f}
Total profit: ₹{total_profit:,.2f}
Overall profit margin: {profit_margin:.2f}%
Average order value: ₹{average_order_value:,.2f}
Best revenue category: {best_category}

Discount analysis:
{discount_analysis.to_string(index=False)}

High-value transaction threshold:
₹{high_value_threshold:,.2f}

High-value transactions:
{high_value_transactions:,}

Do not invent information.
Identify important business trends, risks, and recommendations.
"""

    return insights, recommendations, ai_prompt


def save_results(insights, recommendations, ai_prompt):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "ai_business_insights.txt"

    with open(output_file, "w", encoding="utf-8") as file:

        file.write("AI-READY BUSINESS INSIGHTS\n")
        file.write("=" * 65 + "\n\n")

        file.write("BUSINESS INSIGHTS\n")
        file.write("-" * 65 + "\n")

        for i, insight in enumerate(insights, 1):
            file.write(f"{i}. {insight}\n\n")

        file.write("\nBUSINESS RECOMMENDATIONS\n")
        file.write("-" * 65 + "\n")

        for i, recommendation in enumerate(recommendations, 1):
            file.write(f"{i}. {recommendation}\n\n")

        file.write("\nLLM-READY PROMPT\n")
        file.write("-" * 65 + "\n")
        file.write(ai_prompt)

    return output_file


def main():

    print("=" * 65)
    print("RETAIL ANALYTICS - AI BUSINESS INSIGHTS")
    print("=" * 65)

    df = load_data()

    print("\nRetail data loaded successfully.")

    insights, recommendations, ai_prompt = (
        generate_business_insights(df)
    )

    print("\nAI-READY BUSINESS INSIGHTS")
    print("-" * 65)

    for i, insight in enumerate(insights, 1):
        print(f"\n{i}. {insight}")

    print("\n\nBUSINESS RECOMMENDATIONS")
    print("-" * 65)

    for i, recommendation in enumerate(recommendations, 1):
        print(f"\n{i}. {recommendation}")

    output_file = save_results(
        insights,
        recommendations,
        ai_prompt
    )

    print("\n" + "=" * 65)
    print("AI INSIGHTS GENERATED SUCCESSFULLY")
    print("=" * 65)

    print(f"\nOutput file:")
    print(output_file)


if __name__ == "__main__":
    main()