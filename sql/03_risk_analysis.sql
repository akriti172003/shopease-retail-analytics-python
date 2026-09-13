USE retail_analytics;

-- ============================================================
-- RETAIL ANALYTICS - RISK / SUSPICIOUS TRANSACTION ANALYSIS
-- ============================================================


-- ============================================================
-- 1. HIGH-VALUE TRANSACTIONS
-- ============================================================

SELECT
    order_id,
    customer_id,
    product_id,
    net_revenue,
    quantity,
    discount_pct,
    profit
FROM retail_master
WHERE net_revenue >
(
    SELECT
        AVG(net_revenue) + 1.5 * STDDEV(net_revenue)
    FROM retail_master
)
ORDER BY net_revenue DESC;


-- ============================================================
-- 2. UNUSUALLY HIGH QUANTITY
-- ============================================================

SELECT
    order_id,
    customer_id,
    product_id,
    quantity,
    net_revenue,
    discount_pct
FROM retail_master
WHERE quantity >= 5
ORDER BY quantity DESC, net_revenue DESC;


-- ============================================================
-- 3. EXTREME DISCOUNT TRANSACTIONS
-- ============================================================

SELECT
    order_id,
    customer_id,
    product_id,
    discount_pct,
    net_revenue,
    profit
FROM retail_master
WHERE discount_pct >= 20
ORDER BY net_revenue DESC;


-- ============================================================
-- 4. CUSTOMER SPENDING ANOMALIES
-- ============================================================

SELECT
    order_id,
    customer_id,
    net_revenue,
    profit
FROM retail_master r
WHERE net_revenue >
(
    SELECT AVG(r2.net_revenue) * 2
    FROM retail_master r2
    WHERE r2.customer_id = r.customer_id
)
ORDER BY net_revenue DESC;


-- ============================================================
-- 5. RISK FLAG SUMMARY
-- ============================================================

SELECT
    COUNT(*) AS total_transactions,

    SUM(
        CASE
            WHEN net_revenue >
            (
                SELECT
                    AVG(net_revenue) + 1.5 * STDDEV(net_revenue)
                    FROM retail_master
            )
            THEN 1
            ELSE 0
        END
    ) AS high_value_transactions,

    SUM(
        CASE
            WHEN quantity >= 5
            THEN 1
            ELSE 0
        END
    ) AS high_quantity_transactions,

    SUM(
        CASE
            WHEN discount_pct >= 20
            THEN 1
            ELSE 0
        END
    ) AS extreme_discount_transactions

FROM retail_master;


-- ============================================================
-- 6. HIGH-RISK TRANSACTION SCORING
-- ============================================================

SELECT
    order_id,
    customer_id,
    net_revenue,
    quantity,
    discount_pct,

    (
        CASE
            WHEN net_revenue >
            (
                SELECT
                    AVG(net_revenue) + 1.5 * STDDEV(net_revenue)
                    FROM retail_master
            )
            THEN 30
            ELSE 0
        END

        +

        CASE
            WHEN quantity >= 5
            THEN 20
            ELSE 0
        END

        +

        CASE
            WHEN discount_pct >= 20
            THEN 15
            ELSE 0
        END

        +

        CASE
            WHEN net_revenue >
            (
                SELECT AVG(r2.net_revenue) * 2
                FROM retail_master r2
                WHERE r2.customer_id = retail_master.customer_id
            )
            THEN 35
            ELSE 0
        END
    ) AS risk_score

FROM retail_master
ORDER BY risk_score DESC, net_revenue DESC;


-- ============================================================
-- 7. HIGH-RISK TRANSACTIONS
-- ============================================================

SELECT *
FROM
(
    SELECT
        order_id,
        customer_id,
        product_id,
        net_revenue,
        quantity,
        discount_pct,

        (
            CASE
                WHEN net_revenue >
                (
                    SELECT
                        AVG(net_revenue) + 1.5 * STDDEV(net_revenue)
                        FROM retail_master
                )
                THEN 30
                ELSE 0
            END

            +

            CASE
                WHEN quantity >= 5
                THEN 20
                ELSE 0
            END

            +

            CASE
                WHEN discount_pct >= 20
                THEN 15
                ELSE 0
            END

            +

            CASE
                WHEN net_revenue >
                (
                    SELECT AVG(r2.net_revenue) * 2
                    FROM retail_master r2
                    WHERE r2.customer_id = retail_master.customer_id
                )
                THEN 35
                ELSE 0
            END
        ) AS risk_score

    FROM retail_master
) AS risk_data

WHERE risk_score >= 60
ORDER BY risk_score DESC, net_revenue DESC;