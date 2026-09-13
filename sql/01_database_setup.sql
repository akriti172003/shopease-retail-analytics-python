USE retail_analytics;

-- ============================================
-- RETAIL ANALYTICS DATABASE SETUP
-- ============================================

DROP TABLE IF EXISTS retail_master;

CREATE TABLE retail_master (
    order_id INT,
    customer_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(12,2),
    discount_pct DECIMAL(5,2),
    order_date DATE,
    year INT,
    month INT,
    month_name VARCHAR(20),
    day_name VARCHAR(20),
    quarter INT,
    product_name VARCHAR(100),
    category VARCHAR(100),
    unit_cost DECIMAL(12,2),
    age INT,
    gender VARCHAR(20),
    city VARCHAR(100),
    age_group VARCHAR(20),
    tenure_years DECIMAL(5,1),
    gross_revenue DECIMAL(14,2),
    discount_amt DECIMAL(14,2),
    net_revenue DECIMAL(14,2),
    cost DECIMAL(14,2),
    profit DECIMAL(14,2),
    profit_margin DECIMAL(8,2),
    discount_bucket VARCHAR(30)
);