#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd

print("NumPy version: ",  np.__version__)
print("Pandas version:",  pd.__version__)


# In[2]:


orders    = pd.read_csv("orders.csv")
products  = pd.read_csv("products.csv")
customers = pd.read_csv("customers.csv")

print("=== ORDERS ===")
orders.info()
orders.describe()



# In[3]:


quantities_arr = orders["quantity"].values       # .values converts to NumPy array
prices_arr     = products["unit_price"].values

print("Total units ordered:",  np.sum(quantities_arr))
print("Avg qty per order:  ",  np.mean(quantities_arr).round(2))
print("Largest single order:", np.max(quantities_arr))
print("Cheapest product: Rs.",  np.min(prices_arr).round(2))
print("Most expensive:   Rs.",  np.max(prices_arr).round(2))
print("Average price:    Rs.",  np.mean(prices_arr).round(2))

# Revenue potential before discounts
avg_order_revenue = np.mean(prices_arr) * np.mean(quantities_arr)
print(f"Avg order revenue estimate: Rs.{avg_order_revenue:,.0f}")

# Percentile breakdown
for p in [25, 50, 75, 90]:
    print(f"  {p}th percentile price: Rs.{np.percentile(prices_arr, p):,.2f}")

#

# "From the percentile output — 75th percentile price is around Rs.3,500.
#  What does this tell the business?"
# → Answer: 75% of products are priced below Rs.3,500.
#   Only 25% are premium tier.


# In[4]:


orders_dirty = orders.copy()  

# Inject 50 null discount values (~5% of rows)
null_idx_disc = np.random.choice(orders_dirty.index, size=50, replace=False)
orders_dirty.loc[null_idx_disc, "discount_pct"] = np.nan

# Inject 30 null quantity values (~3% of rows)
null_idx_qty  = np.random.choice(orders_dirty.index, size=30, replace=False)
orders_dirty.loc[null_idx_qty, "quantity"] = np.nan

print(f"Dirty dataset shape  : {orders_dirty.shape}")
print(f"Nulls per column:\n{orders_dirty.isnull().sum()}")



# In[5]:


# ============================================================
# Step 7: Data Cleaning (20 min)
# 
# ============================================================

# 🖊️ TYPE — Step 7: Remove duplicates and fill nulls

# 1. Remove duplicates
orders_clean = orders_dirty.drop_duplicates()
print(f"After removing duplicates: {orders_clean.shape}")   # Back to (1000, 6)

# 2. Inspect remaining nulls
print(f"Nulls before fix:\n{orders_clean.isnull().sum()}")

# Fill discount nulls with 0
# Business logic: if no discount was recorded, none was applied
orders_clean["discount_pct"] = orders_clean["discount_pct"].fillna(0)

# 
median_qty = orders_clean["quantity"].median()
orders_clean["quantity"] = orders_clean["quantity"].fillna(median_qty)

print(f"Nulls after fix:\n{orders_clean.isnull().sum()}")
print(f"Final clean shape: {orders_clean.shape}")




# In[6]:


# ============================================================
# Step 8: Date Handling and Feature Engineering (20 min)
# 

orders_clean["order_date"] = pd.to_datetime(orders_clean["order_date"])
customers["join_date"]     = pd.to_datetime(customers["join_date"])

print("order_date dtype:", orders_clean["order_date"].dtype)
# datetime64[us] — now a proper datetime

# Extract 5 analysis columns from one date
orders_clean["year"]       = orders_clean["order_date"].dt.year
orders_clean["month"]      = orders_clean["order_date"].dt.month
orders_clean["month_name"] = orders_clean["order_date"].dt.strftime("%b")
orders_clean["day_name"]   = orders_clean["order_date"].dt.day_name()
orders_clean["quarter"]    = orders_clean["order_date"].dt.quarter

orders_clean[["order_date","year","month","month_name",
               "day_name","quarter"]].head(8)




# In[7]:


# ------------------------------------------------------------
# 🖊️ TYPE — Step 8b: Customer tenure feature
#.

# How long has each customer been with ShopEase?
today = pd.Timestamp("2024-12-31")

customers["tenure_days"]  = (today - customers["join_date"]).dt.days
customers["tenure_years"] = (customers["tenure_days"] / 365).round(1)

customers[["customer_id","join_date","tenure_days","tenure_years"]].head()



# In[8]:


# ------------------------------------------------------------
# 🖊️ TYPE — Step 8c: Age group segmentation with apply()
# ------------------------------------------------------------

# ── Method 1: Define a function, apply it to each value ───────────────────
def age_group(age):
    if age < 25:   return "18-24"
    elif age < 35: return "25-34"
    elif age < 45: return "35-44"
    else:          return "45+"

customers["age_group"] = customers["age"].apply(age_group)
print(customers["age_group"].value_counts())

# ── Method 2: Lambda — same result, more compact ──────────────────────────
customers["age_group"] = customers["age"].apply(
    lambda x: "18-24" if x < 25 else "25-34" if x < 35 else "35-44" if x < 45 else "45+"
)

# ── Method 3: np.select — FASTEST for large datasets ─────────────────────
conditions = [customers["age"] < 25, customers["age"] < 35, customers["age"] < 45]
choices    = ["18-24", "25-34", "35-44"]
customers["age_group"] = np.select(conditions, choices, default="45+")




# In[9]:


# ============================================================
# Step 9: Build the Master Analysis Table (10 min)

master = pd.merge(orders_clean, products,
                  how="inner", on="product_id")
print("After orders + products:", master.shape)

# Merge with customer details
master = pd.merge(master,
                  customers[["customer_id","age","gender",
                              "city","age_group","tenure_years"]],
                  how="inner", on="customer_id")
print("After + customers      :", master.shape)
print("Columns:", list(master.columns))


# In[10]:


# ------------------------------------------------------------
# 🖊️ TYPE — Step 9b: Calculate revenue and profit columns
# ------------------------------------------------------------

# 

# 🔢 Formulas:
#    gross_revenue = quantity × unit_price
#    discount_amt  = gross_revenue × (discount_pct / 100)
#    net_revenue   = gross_revenue − discount_amt
#    cost          = quantity × unit_cost
#    profit        = net_revenue − cost
#    profit_margin = (profit / net_revenue) × 100

# All 1000 rows calculated simultaneously — no loop
master["gross_revenue"] = master["quantity"] * master["unit_price"]
master["discount_amt"]  = master["gross_revenue"] * (master["discount_pct"] / 100)
master["net_revenue"]   = master["gross_revenue"] - master["discount_amt"]
master["cost"]          = master["quantity"] * master["unit_cost"]
master["profit"]        = master["net_revenue"] - master["cost"]
master["profit_margin"] = np.round((master["profit"] / master["net_revenue"]) * 100, 2)

master[["order_id","quantity","unit_price","discount_pct",
        "gross_revenue","net_revenue","profit","profit_margin"]].head(5)




# In[11]:


print("=" * 55)
print("  SHOPEASE INDIA — 2024 ANNUAL SUMMARY")
print("=" * 55)
print(f"  Total Orders      : {master['order_id'].nunique():,}")
print(f"  Total Customers   : {master['customer_id'].nunique():,}")
print(f"  Gross Revenue     : Rs.{master['gross_revenue'].sum():,.0f}")
print(f"  Total Discounts   : Rs.{master['discount_amt'].sum():,.0f}")
print(f"  Net Revenue       : Rs.{master['net_revenue'].sum():,.0f}")
print(f"  Total Profit      : Rs.{master['profit'].sum():,.0f}")
print(f"  Avg Order Value   : Rs.{master['net_revenue'].mean():,.0f}")
print(f"  Avg Profit Margin : {master['profit_margin'].mean():.1f}%")
print("=" * 55)



# In[12]:


monthly = master.groupby(["month","month_name"]).agg(
    total_orders  = ("order_id",    "count"),
    net_revenue   = ("net_revenue", "sum"),
    total_profit  = ("profit",      "sum"),
    avg_order_val = ("net_revenue", "mean")
).reset_index().sort_values("month")

monthly["net_revenue"]   = monthly["net_revenue"].round(0)
monthly["avg_order_val"] = monthly["avg_order_val"].round(0)

print(monthly[["month_name","total_orders",
               "net_revenue","avg_order_val"]].to_string(index=False))

# Automatically identify best and worst months
best  = monthly.loc[monthly["net_revenue"].idxmax(), "month_name"]
worst = monthly.loc[monthly["net_revenue"].idxmin(), "month_name"]
print(f"Best Month: {best}  |  Worst Month: {worst}")



# In[13]:


# ============================================================
# Steps 12-13: Category and City Analysis — Q2 & Q3 (12 min)
# 

# ------------------------------------------------------------
# 🖊️ TYPE — Step 12: Category performance — answering Q2
# ------------------------------------------------------------

category_perf = master.groupby("category").agg(
    total_orders = ("order_id",       "count"),
    units_sold   = ("quantity",       "sum"),
    net_revenue  = ("net_revenue",    "sum"),
    total_profit = ("profit",         "sum"),
    avg_margin   = ("profit_margin",  "mean")
).reset_index().sort_values("net_revenue", ascending=False)

print(category_perf.to_string(index=False))

print(f"Top by Revenue : {category_perf.iloc[0]['category']}")
print(f"Top by Margin  : {category_perf.loc[category_perf['avg_margin'].idxmax(), 'category']}")

# ===========================================================================
# 💡 EXPLAIN — The revenue vs margin insight — pause here
# ===========================================================================

# "The top category by revenue is NOT always the most profitable one."
# "High revenue with thin margins might be worse for the business than
#  moderate revenue with fat margins."
# "This is a real strategic decision: do you optimise for volume or profit?"
# "You just found this insight in 8 lines of code.
#  In Excel, this would take an hour."


# In[14]:


# ------------------------------------------------------------
# 🖊️ TYPE — Step 13: City-wise analysis — part of Q3
# ------------------------------------------------------------

# 💡 nunique() vs count():
#    count()   → total rows (orders)
#    nunique() → distinct IDs (unique customers)
#    Always use nunique() for customer counts!

city_analysis = master.groupby("city").agg(
    unique_customers = ("customer_id", "nunique"),
    total_orders     = ("order_id",    "count"),
    net_revenue      = ("net_revenue", "sum"),
    avg_order_value  = ("net_revenue", "mean"),
    total_profit     = ("profit",      "sum")
).reset_index().sort_values("net_revenue", ascending=False)

# Derived metric: engagement per customer
city_analysis["orders_per_cust"] = (
    city_analysis["total_orders"] / city_analysis["unique_customers"]
).round(1)

print(city_analysis.to_string(index=False))




# In[15]:


# ============================================================
# Steps 14-15: Customer Segments and Lifetime Value — Q3 & Q6 (12 min)
# ⏱️ TIMING — 12 min | Step 15 is the most complex query.
#             Explain the 2-step pattern before typing.
# ============================================================

# 🖊️ TYPE — Step 14: Age group × gender — deep dive into Q3

# 🎯 This is how marketers make targeting decisions:
#    Which age-gender combo has the highest avg_spend?
#    → That segment gets premium ad spend.

segment = master.groupby(["age_group","gender"]).agg(
    customers = ("customer_id", "nunique"),
    orders    = ("order_id",    "count"),
    revenue   = ("net_revenue", "sum"),
    avg_spend = ("net_revenue", "mean")
).reset_index().sort_values("revenue", ascending=False)

segment["revenue"]   = segment["revenue"].round(0)
segment["avg_spend"] = segment["avg_spend"].round(0)

print(segment.to_string(index=False))


# In[16]:


# ------------------------------------------------------------
# 💡 EXPLAIN — Before Step 15 — set up the two-step mental model
# ------------------------------------------------------------

# "Step 15 has two parts and students often get lost. Explain before typing:"

# Part 1: groupby on customer_id
#   → Collapses all orders into ONE row per customer
#   → Each row = one customer's lifetime summary:
#     total orders, total revenue, first/last purchase

# Part 2: merge with customers table
#   → Adds back name, city, gender, age
#   → The groupby REMOVES all customer details. The merge PUTS THEM BACK.

# "Why not include them in the groupby?
#  Because city and gender don't aggregate — they just describe."

# ------------------------------------------------------------
# 🖊️ TYPE — Step 15: Top 10 customers by lifetime value — answering Q6
# ------------------------------------------------------------

customer_ltv = master.groupby("customer_id").agg(
    total_orders  = ("order_id",    "count"),
    total_revenue = ("net_revenue", "sum"),
    total_profit  = ("profit",      "sum"),
    avg_order_val = ("net_revenue", "mean"),
    first_order   = ("order_date",  "min"),
    last_order    = ("order_date",  "max")
).reset_index()

# Merge back with customer details to get city, gender, age
customer_ltv = pd.merge(customer_ltv,
                        customers[["customer_id","age","gender","city"]],
                        on="customer_id")

customer_ltv = customer_ltv.sort_values("total_revenue", ascending=False)
top10 = customer_ltv.head(10)
top10["total_revenue"] = top10["total_revenue"].round(0)

print("TOP 10 CUSTOMERS BY LIFETIME VALUE:")
print(top10[["customer_id","city","gender","age",
             "total_orders","total_revenue","avg_order_val"]].to_string(index=False))

# ===========================================================================
# 🤖 AI PROMPT — Use AI for a real business discussion
# ===========================================================================

# Prompt: "Our top customer has the highest total revenue but only 12 orders.
#          Another customer has 25 orders but 40% less revenue.
#          Which one is more valuable to us long-term, and why?"

# Let students read the AI response, then debate:
# "Do you agree with AI? What did it miss?"
# → This is the kind of discussion that happens in actual product
#   and strategy meetings.


# In[17]:


# ============================================================
# Steps 16-18: Day-of-Week, Discount Impact, Quarterly (12 min)
# ==========================================================

# "Step 16: What day of the week gets the most orders?"
# "You have day_name in master. Write the groupby yourself — 3 minutes,
#  then we compare."
# → Walk the room. After 3 min, show the solution.

# ------------------------------------------------------------
# 🖊️ TYPE — Step 16: Day-of-week sales pattern
# ------------------------------------------------------------

day_order = ["Monday","Tuesday","Wednesday","Thursday",
             "Friday","Saturday","Sunday"]

dow = master.groupby("day_name").agg(
    orders      = ("order_id",    "count"),
    net_revenue = ("net_revenue", "sum"),
    avg_order   = ("net_revenue", "mean")
# reindex forces natural day order instead of alphabetical
).reindex(day_order).reset_index()

busiest_day = dow.loc[dow["orders"].idxmax(), "day_name"]

print(dow.to_string(index=False))
print(f"Busiest Day: {busiest_day}")

# ===========================================================================
# 💡 EXPLAIN — Why .reindex() is a real-world trick
# ===========================================================================

# "Without reindex(), Pandas sorts day names alphabetically:
#  Friday, Monday, Saturday..."
# "reindex(day_order) forces a custom sort order."
# "You will use this pattern any time you need a non-alphabetical sort:
#  months, custom priority levels, age groups."


# In[18]:


# ------------------------------------------------------------
# 🖊️ TYPE — Step 17: Discount impact analysis — new concept: pd.cut()
# ------------------------------------------------------------

# 💡 pd.cut() bins continuous values into labelled groups.
#    Without it, groupby would make one group per unique discount value
#    (0, 5, 10, 15, 20) — which already happens to be clean here.
#    In real data, you might have 0.0, 0.5, 1.2, 2.7... pd.cut() solves that.

# ❓ Key question: Do bigger discounts actually generate more profit?
#    Or do they just eat into margins?

bins   = [-1, 0, 5, 10, 15, 20]
labels = ["No Discount", "5%", "10%", "15%", "20%"]
master["discount_bucket"] = pd.cut(master["discount_pct"],
                                    bins=bins, labels=labels)

disc_analysis = master.groupby("discount_bucket", observed=True).agg(
    orders        = ("order_id",      "count"),
    net_revenue   = ("net_revenue",   "sum"),
    avg_margin    = ("profit_margin", "mean"),
    total_profit  = ("profit",        "sum")
).reset_index().round(0)

print("Discount Impact on Revenue and Profit:")
print(disc_analysis.to_string(index=False))




# In[19]:


# ------------------------------------------------------------
# 🖊️ TYPE — Step 18: Quarterly performance
# ------------------------------------------------------------

# 🎯 Quarters are the standard unit of business reporting.
#    Q1 vs Q4 comparison tells you if the business is growing.

quarterly = master.groupby("quarter").agg(
    orders      = ("order_id",     "count"),
    net_revenue = ("net_revenue",  "sum"),
    profit      = ("profit",       "sum"),
    avg_margin  = ("profit_margin","mean")
).reset_index()

quarterly.columns = ["Quarter","Orders","Net Revenue","Profit","Avg Margin"]
quarterly[["Net Revenue","Profit"]] = quarterly[["Net Revenue","Profit"]].round(0)
quarterly["Avg Margin"] = quarterly["Avg Margin"].round(1)

print(quarterly.to_string(index=False))


# In[20]:


# ============================================================
# Steps 19-20: Product Stars and Executive Summary (12 min)
# ⏱
# ============================================================

# 🖊️ TYPE — Step 19: Star products and slow movers

# 🎯 Stars      → high revenue, high profit → increase inventory, promote more
#    Slow movers → low revenue, low profit  → consider discounting or delisting

product_perf = master.groupby(["product_id","product_name","category"]).agg(
    units_sold  = ("quantity",    "sum"),
    net_revenue = ("net_revenue", "sum"),
    profit      = ("profit",      "sum")
).reset_index().sort_values("net_revenue", ascending=False)

print("⭐ TOP 5 PRODUCTS (by Revenue):")
print(product_perf.head(5)[["product_name","category",
                              "units_sold","net_revenue","profit"]].to_string(index=False))

print("\n🐢 BOTTOM 5 PRODUCTS (Slow Movers):")
print(product_perf.tail(5)[["product_name","category",
                              "units_sold","net_revenue","profit"]].to_string(index=False))

# ===========================================================================
# 💡 EXPLAIN — The business value of slow mover detection
# ===========================================================================

# "Bottom 5 products are candidates for three actions:
#  discontinue, discount to clear stock, or reposition."
# "Finding these with 8 lines of code vs manually scanning thousands
#  of Excel rows — that is the analyst's value."
# "A data analyst who can answer 'which products should we discontinue?'
#  in 5 minutes is worth hiring."


# In[21]:


# ------------------------------------------------------------
# 🖊️ TYPE — Step 20: Final executive summary — NumPy returns
# ------------------------------------------------------------

# Pull raw NumPy arrays from Pandas columns
rev_arr    = master["net_revenue"].values
profit_arr = master["profit"].values
qty_arr    = master["quantity"].values

print("=" * 60)
print("  SHOPEASE INDIA — EXECUTIVE SUMMARY (FY 2024)")
print("=" * 60)
print(f"  Total Transactions      : {len(rev_arr):,}")
print(f"  Total Net Revenue       : Rs.{np.sum(rev_arr):>15,.0f}")
print(f"  Total Profit            : Rs.{np.sum(profit_arr):>15,.0f}")
print(f"  Avg Order Value         : Rs.{np.mean(rev_arr):>15,.0f}")
print(f"  Median Order Value      : Rs.{np.median(rev_arr):>15,.0f}")
print(f"  Std Dev (Order Values)  : Rs.{np.std(rev_arr):>15,.0f}")
print(f"  Overall Profit Margin   :  {(np.sum(profit_arr)/np.sum(rev_arr)*100):>13.1f}%")
print(f"  Total Units Sold        : {np.sum(qty_arr):>16,}")
print("=" * 60)

# Revenue distribution
p25 = np.percentile(rev_arr, 25)
p75 = np.percentile(rev_arr, 75)
print(f"  25th Percentile         : Rs.{p25:,.0f}")
print(f"  75th Percentile         : Rs.{p75:,.0f}")
print(f"  IQR                     : Rs.{(p75-p25):,.0f}")
print("=" * 60)



# In[ ]:




