USE retail_analytics;

-- ============================================================
-- RETAIL ANALYTICS - BUSINESS ANALYSIS
-- ============================================================


-- ============================================================
-- 1. OVERALL BUSINESS KPIs
-- ============================================================

SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(SUM(net_revenue), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(net_revenue), 2) AS average_order_value,
    ROUND(
        SUM(profit) / SUM(net_revenue) * 100,
        2
    ) AS overall_profit_margin
FROM retail_master;


-- ============================================================
-- 2. MONTHLY SALES & PROFIT PERFORMANCE
-- ============================================================

SELECT
    year,
    month,
    month_name,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(net_revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(
        SUM(profit) / SUM(net_revenue) * 100,
        2
    ) AS profit_margin
FROM retail_master
GROUP BY
    year,
    month,
    month_name
ORDER BY
    year,
    month;


-- ============================================================
-- 3. CATEGORY PERFORMANCE
-- ============================================================

SELECT
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(net_revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(
        SUM(profit) / SUM(net_revenue) * 100,
        2
    ) AS profit_margin
FROM retail_master
GROUP BY category
ORDER BY revenue DESC;


-- ============================================================
-- 4. TOP 10 PRODUCTS BY REVENUE
-- ============================================================

SELECT
    product_id,
    product_name,
    category,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(net_revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit
FROM retail_master
GROUP BY
    product_id,
    product_name,
    category
ORDER BY revenue DESC
LIMIT 10;


-- ============================================================
-- 5. TOP 10 CUSTOMERS BY REVENUE
-- ============================================================

SELECT
    customer_id,
    city,
    age_group,
    gender,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(net_revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit
FROM retail_master
GROUP BY
    customer_id,
    city,
    age_group,
    gender
ORDER BY revenue DESC
LIMIT 10;


-- ============================================================
-- 6. CITY PERFORMANCE
-- ============================================================

SELECT
    city,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(net_revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(
        SUM(profit) / SUM(net_revenue) * 100,
        2
    ) AS profit_margin
FROM retail_master
GROUP BY city
ORDER BY revenue DESC;


-- ============================================================
-- 7. CUSTOMER SEGMENT PERFORMANCE
-- ============================================================

SELECT
    age_group,
    gender,
    COUNT(DISTINCT customer_id) AS customers,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(net_revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit
FROM retail_master
GROUP BY
    age_group,
    gender
ORDER BY revenue DESC;


-- ============================================================
-- 8. DISCOUNT IMPACT ANALYSIS
-- ============================================================

SELECT
    discount_pct,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(net_revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(
        SUM(profit) / SUM(net_revenue) * 100,
        2
    ) AS profit_margin
FROM retail_master
GROUP BY discount_pct
ORDER BY discount_pct;


-- ============================================================
-- 9. QUARTERLY PERFORMANCE
-- ============================================================

SELECT
    year,
    quarter,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(net_revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(
        SUM(profit) / SUM(net_revenue) * 100,
        2
    ) AS profit_margin
FROM retail_master
GROUP BY
    year,
    quarter
ORDER BY
    year,
    quarter;


-- ============================================================
-- 10. DAY-OF-WEEK PERFORMANCE
-- ============================================================

SELECT
    day_name,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(net_revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit
FROM retail_master
GROUP BY day_name
ORDER BY revenue DESC;