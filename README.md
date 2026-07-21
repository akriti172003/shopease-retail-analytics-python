# ShopEase India — Retail Analytics Pipeline (Python | Pandas | NumPy)

An end-to-end retail data analysis project that transforms raw, messy transactional data into business-ready insights — built to simulate how a Data Analyst would approach revenue, profitability, and customer analysis for an e-commerce business.

## What This Project Does

Using a simulated dataset of 1,000+ orders across 20 products and 50 customers, this project:

- **Cleans and validates data** — handles missing values (nulls in discount and quantity fields), removes duplicates, and applies business logic for imputation (e.g., missing discounts treated as 0, missing quantities filled with median).
- **Engineers features** — extracts year, month, quarter, and day-of-week from order dates; calculates customer tenure; segments customers into age groups using three different methods (function, lambda, `np.select`).
- **Merges multi-source data** — joins Orders, Products, and Customers into a single master table for unified analysis.
- **Calculates core business metrics** — gross revenue, discounts, net revenue, cost, profit, and profit margin, computed across all 1,000 transactions simultaneously using vectorized Pandas/NumPy operations (no loops).
- **Delivers business insights**, including:
  - Monthly and quarterly revenue/profit trends (best vs. worst performing months)
  - Category-level performance (revenue leaders vs. margin leaders — and why they're not always the same category)
  - City-wise customer engagement and revenue contribution
  - Age × gender customer segmentation for targeting decisions
  - Top 10 customers by lifetime value
  - Day-of-week sales patterns
  - Discount-bucket impact analysis (do bigger discounts actually hurt profit?)
  - Top 5 and bottom 5 products by revenue (stars vs. slow movers)
  - A final executive summary with key statistics (mean, median, std dev, percentiles)

## Key Results

```
Total Transactions      : 1,000
Total Net Revenue       : Rs. 59,94,656
Total Profit             : Rs. 24,48,274
Overall Profit Margin    : 40.8%
```

## Tech Stack

- **Python 3.13**
- **Pandas** — data cleaning, merging, grouping, aggregation
- **NumPy** — vectorized numerical computation, percentiles, statistical summaries

## Files in This Repo

| File | Description |
|---|---|
| `Day2_Learn_python_using_AI.ipynb` | Full analysis notebook, step-by-step |
| `main.py` | Script version of the same analysis |
| `orders.csv` | Order-level transaction data |
| `products.csv` | Product catalog with pricing and cost |
| `customers.csv` | Customer demographic and signup data |

## What This Demonstrates

- Comfort with the full data analysis lifecycle: ingest → clean → transform → merge → analyze → report
- Ability to translate raw transactional data into decision-ready business metrics (revenue vs. margin trade-offs, customer value, product performance)
- Practical use of Pandas' `groupby`, `merge`, `pivot`-style aggregation, and NumPy for fast numerical computation on large datasets — the same techniques used in real MIS, business intelligence, and analytics reporting workflows.