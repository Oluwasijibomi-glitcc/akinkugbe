USE walmart_app;

SET GLOBAL local_infile = 1;
SET SESSION sql_safe_updates = 0;

-- 1. CUSTOMER
LOAD DATA LOCAL INFILE 'C:/Users/Pari Goyal/PycharmProjects/bigdataproject/data/walmart_oltp/loading/customer.csv'
INTO TABLE customer
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(customer_id, first_name, last_name, email,
 zip_code, date_joined, channel_signup, loyalty_tier);

-- 2. PRODUCT
LOAD DATA LOCAL INFILE 'C:/Users/Pari Goyal/PycharmProjects/bigdataproject/data/walmart_oltp/loading/product.csv'
INTO TABLE product
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(product_id, sku, product_name, category,
 sub_category, base_price, is_active);

-- 3. STORE
LOAD DATA LOCAL INFILE 'C:/Users/Pari Goyal/PycharmProjects/bigdataproject/data/walmart_oltp/loading/store.csv'
INTO TABLE store
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(store_id, store_name, store_type, city, state, zip_code, region);

-- 4. PAYMENT METHOD
LOAD DATA LOCAL INFILE 'C:/Users/Pari Goyal/PycharmProjects/bigdataproject/data/walmart_oltp/loading/payment_method.csv'
INTO TABLE payment_method
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(payment_method_id, method_name);

-- 5. PROMOTION
LOAD DATA LOCAL INFILE 'C:/Users/Pari Goyal/PycharmProjects/bigdataproject/data/walmart_oltp/loading/promotion.csv'
INTO TABLE promotion
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(promo_id, promo_name, promo_type, discount_value,
 start_date, end_date, min_basket_amount, target_channel, is_active);

-- 6. TRANSACTION HEADER
LOAD DATA LOCAL INFILE 'C:/Users/Pari Goyal/PycharmProjects/bigdataproject/data/walmart_oltp/loading/transaction_header.csv'
INTO TABLE transaction_header
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(transaction_id_raw,
 transaction_id,
 customer_id,
 store_id,
 transaction_timestamp,
 channel,
 total_amount,
 payment_method_id,
 payment_method);

-- 7. TRANSACTION LINE ITEM
LOAD DATA LOCAL INFILE 'C:/Users/Pari Goyal/PycharmProjects/bigdataproject/data/walmart_oltp/loading/transaction_line_item.csv'
INTO TABLE transaction_line_item
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(line_item_id, transaction_id, product_id,
 quantity, unit_price, discount_amount, promo_id);

-- 8. CUSTOMER LOYALTY PROFILE
LOAD DATA LOCAL INFILE 'C:/Users/Pari Goyal/PycharmProjects/bigdataproject/data/walmart_oltp/loading/customer_loyalty_profile.csv'
INTO TABLE customer_loyalty_profile
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(customer_id, loyalty_tier, points_balance,
 enrollment_date, last_activity_date, lifetime_spend);

-- 9. PROMOTION ELIGIBILITY  (AI column excluded)
LOAD DATA LOCAL INFILE 'C:/Users/Pari Goyal/PycharmProjects/bigdataproject/data/walmart_oltp/loading/promotion_eligibility.csv'
INTO TABLE promotion_eligibility
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(promo_id, customer_id, eligibility_start_date,
 eligibility_end_date, eligibility_reason);

-- 10. INVENTORY SNAPSHOT  (AI column excluded)
LOAD DATA LOCAL INFILE 'C:/Users/Pari Goyal/PycharmProjects/bigdataproject/data/walmart_oltp/loading/inventory_snapshot.csv'
INTO TABLE inventory_snapshot
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(store_id, product_id, snapshot_date,
 stock_level, reorder_point, on_order_qty);

SELECT * FROM customer;

-- ============================================
-- 1. LOAD product_sustainability
-- ============================================

LOAD DATA LOCAL INFILE
'C:/Users/Pari Goyal/PycharmProjects/bigdataproject/data/walmart_oltp/loading/product_sustainability.csv'
INTO TABLE product_sustainability
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(product_id,
 overall_score,
 carbon_kg_per_unit,
 water_liters_per_unit,
 packaging_type,
 is_local,
 last_updated);

-- ============================================
-- 2. LOAD customer_sustainability_profile
-- ============================================

LOAD DATA LOCAL INFILE
'C:/Users/Pari Goyal/PycharmProjects/bigdataproject/data/walmart_oltp/loading/customer_sustainability_profile.csv'
INTO TABLE customer_sustainability_profile
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(customer_id,
 overall_sustainability_goal,
 weight_environment,
 weight_price_sensitivity,
 weight_brand_loyalty,
 receive_recommendations);

-- ============================================
-- 3. VALIDATION QUERIES
-- ============================================

SELECT COUNT(*) AS product_sustainability_rows
FROM product_sustainability;

SELECT COUNT(*) AS customer_sustainability_profile_rows
FROM customer_sustainability_profile;

SELECT p.product_id,
       p.product_name,
       ps.overall_score,
       ps.packaging_type,
       ps.is_local
FROM product p
JOIN product_sustainability ps
  ON p.product_id = ps.product_id
LIMIT 10;

SELECT c.customer_id,
       clp.loyalty_tier,
       csp.overall_sustainability_goal,
       csp.weight_environment
FROM customer c
JOIN customer_loyalty_profile clp
  ON c.customer_id = clp.customer_id
JOIN customer_sustainability_profile csp
  ON c.customer_id = csp.customer_id
LIMIT 10;
