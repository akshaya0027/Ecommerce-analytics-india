-- ============================================================
-- E-COMMERCE CUSTOMER & SALES ANALYTICS — SQL ANALYSIS
-- Database: ecommerce.db (SQLite / DB Browser for SQLite)
-- Tables: orders, customers
-- ============================================================

-- 1. Total revenue, total orders, and average order value
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(net_amount), 2) AS total_revenue,
    ROUND(AVG(net_amount), 2) AS avg_order_value
FROM orders
WHERE order_status = 'Delivered';

-- 2. Monthly revenue trend
SELECT
    strftime('%Y-%m', order_date) AS order_month,
    COUNT(order_id) AS orders,
    ROUND(SUM(net_amount), 2) AS revenue
FROM orders
WHERE order_status = 'Delivered'
GROUP BY order_month
ORDER BY order_month;

-- 3. Revenue and order count by category
SELECT
    category,
    COUNT(order_id) AS orders,
    ROUND(SUM(net_amount), 2) AS revenue,
    ROUND(AVG(net_amount), 2) AS avg_order_value
FROM orders
WHERE order_status = 'Delivered'
GROUP BY category
ORDER BY revenue DESC;

-- 4. Top 10 cities by revenue
SELECT
    c.city,
    c.city_tier,
    COUNT(o.order_id) AS orders,
    ROUND(SUM(o.net_amount), 2) AS revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'Delivered'
GROUP BY c.city, c.city_tier
ORDER BY revenue DESC
LIMIT 10;

-- 5. Revenue by city tier
SELECT
    c.city_tier,
    COUNT(o.order_id) AS orders,
    ROUND(SUM(o.net_amount), 2) AS revenue,
    ROUND(AVG(o.net_amount), 2) AS avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'Delivered'
GROUP BY c.city_tier
ORDER BY revenue DESC;

-- 6. Payment method distribution
SELECT
    payment_method,
    COUNT(order_id) AS orders,
    ROUND(100.0 * COUNT(order_id) / (SELECT COUNT(*) FROM orders), 2) AS pct_of_orders
FROM orders
GROUP BY payment_method
ORDER BY orders DESC;

-- 7. Order status breakdown (cancellation / return rate)
SELECT
    order_status,
    COUNT(order_id) AS orders,
    ROUND(100.0 * COUNT(order_id) / (SELECT COUNT(*) FROM orders), 2) AS pct_of_orders
FROM orders
GROUP BY order_status
ORDER BY orders DESC;

-- 8. Return rate by category (which products get returned most?)
SELECT
    category,
    SUM(CASE WHEN order_status = 'Returned' THEN 1 ELSE 0 END) AS returned_orders,
    COUNT(order_id) AS total_orders,
    ROUND(100.0 * SUM(CASE WHEN order_status = 'Returned' THEN 1 ELSE 0 END) / COUNT(order_id), 2) AS return_rate_pct
FROM orders
GROUP BY category
ORDER BY return_rate_pct DESC;

-- 9. Top 10 best-selling products by revenue
SELECT
    product_name,
    category,
    COUNT(order_id) AS times_ordered,
    SUM(quantity) AS total_units,
    ROUND(SUM(net_amount), 2) AS revenue
FROM orders
WHERE order_status = 'Delivered'
GROUP BY product_name, category
ORDER BY revenue DESC
LIMIT 10;

-- 10. Customer order frequency distribution (how many customers ordered N times)
SELECT
    order_count,
    COUNT(*) AS num_customers
FROM (
    SELECT customer_id, COUNT(order_id) AS order_count
    FROM orders
    GROUP BY customer_id
) t
GROUP BY order_count
ORDER BY order_count;

-- 11. RFM base query — Recency, Frequency, Monetary per customer
-- (Reference date = day after the last order in the dataset)
WITH ref_date AS (
    SELECT date(MAX(order_date), '+1 day') AS max_date FROM orders
)
SELECT
    o.customer_id,
    CAST(julianday((SELECT max_date FROM ref_date)) - julianday(MAX(o.order_date)) AS INTEGER) AS recency_days,
    COUNT(o.order_id) AS frequency,
    ROUND(SUM(o.net_amount), 2) AS monetary
FROM orders o
WHERE o.order_status = 'Delivered'
GROUP BY o.customer_id
ORDER BY monetary DESC;

-- 12. Gender-wise spending pattern
SELECT
    c.gender,
    COUNT(o.order_id) AS orders,
    ROUND(SUM(o.net_amount), 2) AS revenue,
    ROUND(AVG(o.net_amount), 2) AS avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'Delivered'
GROUP BY c.gender;

-- 13. Day-of-week order pattern
SELECT
    CASE CAST(strftime('%w', order_date) AS INTEGER)
        WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday' END AS day_of_week,
    COUNT(order_id) AS orders,
    ROUND(SUM(net_amount), 2) AS revenue
FROM orders
WHERE order_status = 'Delivered'
GROUP BY day_of_week
ORDER BY orders DESC;
