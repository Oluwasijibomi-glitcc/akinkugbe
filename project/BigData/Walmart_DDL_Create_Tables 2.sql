-- Create schema for the project
DROP DATABASE walmart_oltp;
CREATE DATABASE IF NOT EXISTS walmart_oltp;
USE walmart_oltp;

-- 1. CUSTOMER
CREATE TABLE customer (
    customer_id        BIGINT PRIMARY KEY,
    first_name         VARCHAR(100),
    last_name          VARCHAR(100),
    email              VARCHAR(255),
    zip_code           VARCHAR(20),
    loyalty_tier       VARCHAR(20),       -- e.g., Bronze/Silver/Gold/Platinum
    date_joined        DATE,
    channel_signup     VARCHAR(20)        -- e.g., WEB, APP, STORE
);

-- 2. PRODUCT
CREATE TABLE product (
    product_id         BIGINT PRIMARY KEY,
    sku                VARCHAR(50) UNIQUE,
    product_name       VARCHAR(255),
    category           VARCHAR(100),
    sub_category       VARCHAR(100),
    base_price         DECIMAL(10,2),
    is_active          TINYINT(1) DEFAULT 1
);

-- 3. STORE
CREATE TABLE store (
    store_id           BIGINT PRIMARY KEY,
    store_name         VARCHAR(255),
    store_type         VARCHAR(50),       -- SUPERCENTER, NEIGHBORHOOD, ONLINE_FULFILLMENT
    city               VARCHAR(100),
    state              VARCHAR(50),
    zip_code           VARCHAR(20),
    region             VARCHAR(50)
);

-- 4. TRANSACTION HEADER
CREATE TABLE transaction_header (
	transaction_id_raw 	   VARCHAR(50),
    transaction_id         BIGINT PRIMARY KEY,
    customer_id            BIGINT,
    store_id               BIGINT,
    transaction_timestamp  DATETIME,
    channel                VARCHAR(20),   -- IN_STORE, WEB, APP
    total_amount           DECIMAL(12,2),
    payment_method         VARCHAR(20),   -- CREDIT_CARD, DEBIT, CASH, WALLET
    CONSTRAINT fk_th_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT fk_th_store
        FOREIGN KEY (store_id) REFERENCES store(store_id)
);

-- 5. TRANSACTION LINE ITEM
CREATE TABLE transaction_line_item (
    line_item_id       BIGINT PRIMARY KEY,
    transaction_id     BIGINT,
    product_id         BIGINT,
    quantity           INT,
    unit_price         DECIMAL(10,2),     -- price at time of purchase (after discount)
    discount_amount    DECIMAL(10,2),     -- total discount applied to this line
    promo_id           BIGINT NULL,       -- nullable FK to promotion
    CONSTRAINT fk_tli_transaction
        FOREIGN KEY (transaction_id) REFERENCES transaction_header(transaction_id),
    CONSTRAINT fk_tli_product
        FOREIGN KEY (product_id) REFERENCES product(product_id)
    -- promo FK added after promotion table is created
);

-- 6. INVENTORY SNAPSHOT
CREATE TABLE inventory_snapshot (
    inventory_snapshot_id  BIGINT PRIMARY KEY auto_increment,
    store_id               BIGINT,
    product_id             BIGINT,
    snapshot_date          DATE,
    stock_level            INT,
    reorder_point          INT,
    on_order_qty           INT,
    CONSTRAINT fk_inv_store
        FOREIGN KEY (store_id) REFERENCES store(store_id),
    CONSTRAINT fk_inv_product
        FOREIGN KEY (product_id) REFERENCES product(product_id)
);

-- 7. PROMOTION
CREATE TABLE promotion (
    promo_id           BIGINT PRIMARY KEY auto_increment,
    promo_name         VARCHAR(255),
    promo_type         VARCHAR(50),       -- PERCENT_DISCOUNT, FIXED_DISCOUNT, BOGO, BUNDLE
    discount_value     DECIMAL(10,2),     -- interpreted based on promo_type
    start_date         DATE,
    end_date           DATE,
    min_basket_amount  DECIMAL(10,2),
    target_channel     VARCHAR(20),       -- ALL, WEB, APP, STORE
    is_active          TINYINT(1) DEFAULT 1
);

-- Add FK from line item to promotion now that promotion exists
ALTER TABLE transaction_line_item
    ADD CONSTRAINT fk_tli_promo
        FOREIGN KEY (promo_id) REFERENCES promotion(promo_id);

-- 8. PROMOTION ELIGIBILITY
CREATE TABLE promotion_eligibility (
    promo_eligibility_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
    promo_id               BIGINT,
    customer_id            BIGINT,
    eligibility_start_date DATE,
    eligibility_end_date   DATE,
    eligibility_reason     VARCHAR(50),   -- LOYALTY_TIER, CAMPAIGN, RECOVERY, etc.
    CONSTRAINT fk_pe_promo
        FOREIGN KEY (promo_id) REFERENCES promotion(promo_id),
    CONSTRAINT fk_pe_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);

-- 9. Customer Loyalty Profile
CREATE TABLE customer_loyalty_profile (
    customer_id        BIGINT PRIMARY KEY,
    loyalty_tier       VARCHAR(20),       -- e.g., BRONZE, SILVER, GOLD, PLATINUM
    points_balance     INT,
    enrollment_date    DATE,
    last_activity_date DATE,
    lifetime_spend     DECIMAL(12,2),
    CONSTRAINT fk_clp_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);

-- 10. Payment Method
CREATE TABLE payment_method (
    payment_method_id  INT PRIMARY KEY,
    method_name        VARCHAR(50)   -- e.g., CREDIT_CARD, DEBIT_CARD, CASH, WALLET
);

ALTER TABLE transaction_header
ADD COLUMN payment_method_id INT,
ADD CONSTRAINT fk_th_pm
    FOREIGN KEY (payment_method_id) REFERENCES payment_method(payment_method_id);