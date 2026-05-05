USE walmart_oltp;

-- Q1: Recent orders for a specific customer, with line details and payment method
SELECT 
    th.transaction_id,
    th.transaction_timestamp,
    c.customer_id,
    c.first_name,
    c.last_name,
    s.store_name,
    pm.method_name AS payment_method,
    p.product_id,
    p.product_name,
    tli.quantity,
    tli.unit_price,
    tli.quantity * tli.unit_price AS line_amount,
    tli.promo_id
FROM transaction_header th
JOIN customer c
    ON th.customer_id = c.customer_id
JOIN store s
    ON th.store_id = s.store_id
JOIN payment_method pm
    ON th.payment_method_id = pm.payment_method_id
JOIN transaction_line_item tli
    ON th.transaction_id = tli.transaction_id
JOIN product p
    ON tli.product_id = p.product_id
WHERE c.customer_id = 12346
ORDER BY th.transaction_timestamp DESC
LIMIT 50;

SET @today := '2024-12-02';

-- Q2: All currently active promotions for a given customer today
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    p.promo_id,
    p.promo_name,
    p.promo_type,
    p.discount_value,
    p.target_channel,
    pe.eligibility_reason,
    p.start_date,
    p.end_date
FROM promotion_eligibility pe
JOIN promotion p
    ON pe.promo_id = p.promo_id
JOIN customer c
    ON pe.customer_id = c.customer_id
WHERE c.customer_id = 12346
	AND p.is_active = 1
  AND @today BETWEEN pe.eligibility_start_date 
                    AND pe.eligibility_end_date
  AND @today BETWEEN p.start_date 
                    AND p.end_date;

-- Q3: Low-stock products at a store based on latest snapshot
SELECT 
    inv.store_id,
    s.store_name,
    inv.product_id,
    p.product_name,
    inv.snapshot_date,
    inv.stock_level,
    inv.reorder_point,
    inv.on_order_qty
FROM inventory_snapshot inv
JOIN store s 
    ON inv.store_id = s.store_id
JOIN product p 
    ON inv.product_id = p.product_id
WHERE inv.store_id = 1
  AND inv.snapshot_date = '2024-11-01'
  AND inv.stock_level <= inv.reorder_point
ORDER BY inv.stock_level ASC
LIMIT 50;

-- Q4: Revenue by payment method for a given date range
SELECT 
    pm.method_name AS payment_method,
    COUNT(DISTINCT th.transaction_id) AS num_transactions,
    SUM(tli.quantity * tli.unit_price) AS total_revenue
FROM transaction_header th
JOIN transaction_line_item tli
    ON th.transaction_id = tli.transaction_id
JOIN payment_method pm
    ON th.payment_method_id = pm.payment_method_id
WHERE th.transaction_timestamp BETWEEN '2009-10-01' AND '2009-12-31'
GROUP BY pm.method_name
ORDER BY total_revenue DESC;

