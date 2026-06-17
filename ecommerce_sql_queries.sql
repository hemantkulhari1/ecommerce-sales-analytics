-- E-Commerce Sales Analytics

CREATE DATABASE IF NOT EXISTS ecommerce_db;
USE ecommerce_db;

DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    order_id         VARCHAR(12)    PRIMARY KEY,
    customer_id      VARCHAR(10)    NOT NULL,
    customer_segment VARCHAR(20),
    order_date       DATE           NOT NULL,
    year             INT,
    month            INT,
    month_name       VARCHAR(15),
    quarter          VARCHAR(5),
    product_name     VARCHAR(60),
    category         VARCHAR(40),
    unit_price       DECIMAL(10,2),
    quantity         INT,
    discount_pct     DECIMAL(5,2),
    discount_amount  DECIMAL(10,2),
    total_price      DECIMAL(10,2),
    shipping_cost    DECIMAL(8,2),
    payment_method   VARCHAR(20),
    order_status     VARCHAR(20),
    city             VARCHAR(30),
    region           VARCHAR(20)
);

-- =============================================

-- OVERALL KPIs

-- Total Revenue, Orders, AOV, Total Units Sold
SELECT
    COUNT(*)                                         AS total_orders,
    COUNT(DISTINCT customer_id)                      AS unique_customers,
    ROUND(SUM(total_price), 2)                       AS total_revenue,
    ROUND(AVG(total_price), 2)                       AS avg_order_value,
    SUM(quantity)                                    AS total_units_sold,
    ROUND(SUM(discount_amount), 2)                   AS total_discount_given,
    ROUND(SUM(shipping_cost), 2)                     AS total_shipping_revenue,
    ROUND(
        SUM(CASE WHEN order_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    )                                                AS return_rate_pct,
    ROUND(
        SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    )                                                AS cancellation_rate_pct
FROM transactions
WHERE order_status IN ('Delivered', 'Returned');  -- exclude pending for revenue KPIs

-- ======================================================

-- REVENUE TREND — Monthly

SELECT
    year,
    month,
    month_name,
    quarter,
    COUNT(*)                        AS total_orders,
    ROUND(SUM(total_price), 2)      AS monthly_revenue,
    ROUND(AVG(total_price), 2)      AS avg_order_value,
    COUNT(DISTINCT customer_id)     AS unique_customers
FROM transactions
WHERE order_status = 'Delivered'
GROUP BY year, month, month_name, quarter
ORDER BY year, month;

-- =============================================

-- REVENUE BY QUARTER & YEAR


SELECT
    year,
    quarter,
    ROUND(SUM(total_price), 2)      AS quarterly_revenue,
    COUNT(*)                        AS total_orders,
    COUNT(DISTINCT customer_id)     AS unique_customers
FROM transactions
WHERE order_status = 'Delivered'
GROUP BY year, quarter
ORDER BY year, quarter;


-- =======================================================

-- CATEGORY PERFORMANCE

SELECT
    category,
    COUNT(*)                                         AS total_orders,
    SUM(quantity)                                    AS units_sold,
    ROUND(SUM(total_price), 2)                       AS total_revenue,
    ROUND(AVG(total_price), 2)                       AS avg_order_value,
    ROUND(AVG(discount_pct) * 100, 2)               AS avg_discount_pct,
    ROUND(
        SUM(total_price) * 100.0 / SUM(SUM(total_price)) OVER (), 2
    )                                                AS revenue_share_pct
FROM transactions
WHERE order_status = 'Delivered'
GROUP BY category
ORDER BY total_revenue DESC;


-- =========================================
-- TOP 10 PRODUCTS BY REVENUE


SELECT
    product_name,
    category,
    COUNT(*)                        AS total_orders,
    SUM(quantity)                   AS units_sold,
    ROUND(SUM(total_price), 2)      AS total_revenue,
    ROUND(AVG(unit_price), 2)       AS avg_unit_price
FROM transactions
WHERE order_status = 'Delivered'
GROUP BY product_name, category
ORDER BY total_revenue DESC
LIMIT 10;


-- ============================================

-- CUSTOMER SEGMENTATION (New vs Returning vs Loyal)


SELECT
    customer_segment,
    COUNT(DISTINCT customer_id)     AS num_customers,
    COUNT(*)                        AS total_orders,
    ROUND(SUM(total_price), 2)      AS total_revenue,
    ROUND(AVG(total_price), 2)      AS avg_order_value,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT customer_id), 2) AS avg_orders_per_customer
FROM transactions
WHERE order_status = 'Delivered'
GROUP BY customer_segment
ORDER BY total_revenue DESC;


-- ===============================================

-- REPEAT CUSTOMER RATE

WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS num_orders
    FROM transactions
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN num_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(
        SUM(CASE WHEN num_orders > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS repeat_customer_rate_pct
FROM customer_orders;


-- ====================================
-- REGIONAL & CITY PERFORMANCE

SELECT
    region,
    city,
    COUNT(*)                        AS total_orders,
    COUNT(DISTINCT customer_id)     AS unique_customers,
    ROUND(SUM(total_price), 2)      AS total_revenue,
    ROUND(AVG(total_price), 2)      AS avg_order_value
FROM transactions
WHERE order_status = 'Delivered'
GROUP BY region, city
ORDER BY total_revenue DESC;


-- ============================================
-- PAYMENT METHOD BREAKDOWN

SELECT
    payment_method,
    COUNT(*)                                         AS total_orders,
    ROUND(SUM(total_price), 2)                       AS total_revenue,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS order_share_pct
FROM transactions
WHERE order_status = 'Delivered'
GROUP BY payment_method
ORDER BY total_orders DESC;


-- =====================================================

-- ORDER STATUS DISTRIBUTION

SELECT
    order_status,
    COUNT(*)                                             AS total_orders,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)  AS percentage
FROM transactions
GROUP BY order_status
ORDER BY total_orders DESC;


-- =====================================================
-- DISCOUNT IMPACT ANALYSIS

SELECT
    CASE
        WHEN discount_pct = 0         THEN 'No Discount'
        WHEN discount_pct <= 0.10     THEN '1–10%'
        WHEN discount_pct <= 0.20     THEN '11–20%'
        WHEN discount_pct <= 0.30     THEN '21–30%'
        ELSE '30%+'
    END AS discount_bucket,
    COUNT(*)                        AS total_orders,
    ROUND(SUM(total_price), 2)      AS total_revenue,
    ROUND(AVG(total_price), 2)      AS avg_order_value
FROM transactions
WHERE order_status = 'Delivered'
GROUP BY discount_bucket
ORDER BY FIELD(discount_bucket, 'No Discount', '1–10%', '11–20%', '21–30%', '30%+');


-- =====================================================
-- YoY REVENUE GROWTH


WITH yearly AS (
    SELECT
        year,
        ROUND(SUM(total_price), 2) AS annual_revenue
    FROM transactions
    WHERE order_status = 'Delivered'
    GROUP BY year
)
SELECT
    year,
    annual_revenue,
    LAG(annual_revenue) OVER (ORDER BY year) AS prev_year_revenue,
    ROUND(
        (annual_revenue - LAG(annual_revenue) OVER (ORDER BY year))
        * 100.0 / LAG(annual_revenue) OVER (ORDER BY year), 2
    ) AS yoy_growth_pct
FROM yearly;


-- ========================================
-- TOP 5 HIGH-VALUE CUSTOMERS (by total spend)


SELECT
    customer_id,
    customer_segment,
    city,
    region,
    COUNT(DISTINCT order_id)        AS total_orders,
    SUM(quantity)                   AS units_purchased,
    ROUND(SUM(total_price), 2)      AS total_spend
FROM transactions
WHERE order_status = 'Delivered'
GROUP BY customer_id, customer_segment, city, region
ORDER BY total_spend DESC
LIMIT 5;
