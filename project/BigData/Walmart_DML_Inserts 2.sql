USE walmart_oltp;

# SHOW GLOBAL VARIABLES LIKE 'local_infile';
# SET GLOBAL local_infile = 1;
SET SESSION sql_safe_updates = 0;

-- 1. CUSTOMER
LOAD DATA LOCAL INFILE '/Users/oluwasijibomiakinkugbe/Desktop/Managing Big Data /Project/data/customer.csv'
INTO TABLE customer
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(customer_id, first_name, last_name, email,
 zip_code, date_joined, channel_signup, loyalty_tier);

-- 2. PRODUCT
LOAD DATA LOCAL INFILE '/Users/oluwasijibomiakinkugbe/Desktop/Managing Big Data /Project/data/product.csv'
# 'C:/data/walmart_oltp/loading/product.csv'
INTO TABLE product
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(product_id, sku, product_name, category,
 sub_category, base_price, is_active);

-- 3. STORE
LOAD DATA LOCAL INFILE '/Users/oluwasijibomiakinkugbe/Desktop/Managing Big Data /Project/data/store.csv'
# 'C:/data/walmart_oltp/loading/store.csv'
INTO TABLE store
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(store_id, store_name, store_type, city, state, zip_code, region);

-- 4. PAYMENT METHOD
LOAD DATA LOCAL INFILE '/Users/oluwasijibomiakinkugbe/Desktop/Managing Big Data /Project/data/payment_method.csv'
# 'C:/data/walmart_oltp/loading/payment_method.csv'
INTO TABLE payment_method
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(payment_method_id, method_name);

-- 5. PROMOTION
LOAD DATA LOCAL INFILE '/Users/oluwasijibomiakinkugbe/Desktop/Managing Big Data /Project/data/promotion.csv'
# 'C:/data/walmart_oltp/loading/promotion.csv'
INTO TABLE promotion
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(promo_id, promo_name, promo_type, discount_value,
 start_date, end_date, min_basket_amount, target_channel, is_active);

-- 6. TRANSACTION HEADER
LOAD DATA LOCAL INFILE '/Users/oluwasijibomiakinkugbe/Desktop/Managing Big Data /Project/data/transaction_header.csv'
# 'C:/data/walmart_oltp/loading/transaction_header.csv'
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
LOAD DATA LOCAL INFILE '/Users/oluwasijibomiakinkugbe/Desktop/Managing Big Data /Project/data/transaction_line_item.csv'
# 'C:/data/walmart_oltp/loading/transaction_line_item.csv'
INTO TABLE transaction_line_item
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(line_item_id, transaction_id, product_id,
 quantity, unit_price, discount_amount, promo_id);

-- 8. CUSTOMER LOYALTY PROFILE
LOAD DATA LOCAL INFILE '/Users/oluwasijibomiakinkugbe/Desktop/Managing Big Data /Project/data/customer_loyalty_profile.csv'
# 'C:/data/walmart_oltp/loading/customer_loyalty_profile.csv'
INTO TABLE customer_loyalty_profile
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(customer_id, loyalty_tier, points_balance,
 enrollment_date, last_activity_date, lifetime_spend);

-- 9. PROMOTION ELIGIBILITY  (AI column excluded)
LOAD DATA LOCAL INFILE '/Users/oluwasijibomiakinkugbe/Desktop/Managing Big Data /Project/data/promotion_eligibility.csv'
# 'C:/data/walmart_oltp/loading/promotion_eligibility.csv'
INTO TABLE promotion_eligibility
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(promo_id, customer_id, eligibility_start_date,
 eligibility_end_date, eligibility_reason);

-- 10. INVENTORY SNAPSHOT  (AI column excluded)
LOAD DATA LOCAL INFILE '/Users/oluwasijibomiakinkugbe/Desktop/Managing Big Data /Project/data/inventory_snapshot.csv'
# 'C:/data/walmart_oltp/loading/inventory_snapshot.csv'
INTO TABLE inventory_snapshot
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(store_id, product_id, snapshot_date,
 stock_level, reorder_point, on_order_qty);

SELECT * FROM customer;