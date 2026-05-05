-- Create DW schema
DROP DATABASE IF EXISTS walmart_dwh;
CREATE DATABASE walmart_dwh;
USE walmart_dwh;

-- 1) Date dimension
CREATE TABLE dim_date (
    date_key        INT PRIMARY KEY,  -- yyyymmdd
    full_date       DATE,
    year            INT,
    quarter         TINYINT,
    month           TINYINT,
    month_name      VARCHAR(20),
    day             TINYINT,
    day_name        VARCHAR(20),
    week_of_year    TINYINT
);

-- 2) Customer dimension
CREATE TABLE dim_customer (
    customer_key    INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     BIGINT,       -- business key from walmart_oltp.customer
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    zip_code        VARCHAR(20),
    region          VARCHAR(50),
    CONSTRAINT uk_dim_customer UNIQUE (customer_id)
);

-- 3) Loyalty tier dimension
CREATE TABLE dim_loyalty_tier (
    loyalty_tier_key INT AUTO_INCREMENT PRIMARY KEY,
    loyalty_tier     VARCHAR(20),
    description      VARCHAR(255),
    CONSTRAINT uk_dim_loyalty UNIQUE (loyalty_tier)
);

-- 4) Sustainability goal dimension
CREATE TABLE dim_sustainability_goal (
    sust_goal_key    INT AUTO_INCREMENT PRIMARY KEY,
    sust_goal_code   ENUM('low','medium','high'),
    description      VARCHAR(255),
    CONSTRAINT uk_dim_sust_goal UNIQUE (sust_goal_code)
);

-- 5) Channel dimension
CREATE TABLE dim_channel (
    channel_key   INT AUTO_INCREMENT PRIMARY KEY,
    channel_code  VARCHAR(20),   -- STORE / WEB / APP / etc.
    description   VARCHAR(255),
    CONSTRAINT uk_dim_channel UNIQUE (channel_code)
);

-- 6) Store dimension
CREATE TABLE dim_store (
    store_key   INT AUTO_INCREMENT PRIMARY KEY,
    store_id    BIGINT,
    store_name  VARCHAR(255),
    store_type  VARCHAR(50),
    city        VARCHAR(100),
    state       VARCHAR(50),
    zip_code    VARCHAR(20),
    region      VARCHAR(50),
    CONSTRAINT uk_dim_store UNIQUE (store_id)
);

-- 7) Product dimension
CREATE TABLE dim_product (
    product_key      INT AUTO_INCREMENT PRIMARY KEY,
    product_id       BIGINT,
    sku              VARCHAR(50),
    product_name     VARCHAR(255),
    category         VARCHAR(100),
    sub_category     VARCHAR(100),
    base_price       DECIMAL(10,2),
    overall_score    INT,              -- from product_sustainability
    packaging_type   VARCHAR(50),
    is_local         TINYINT(1),
    CONSTRAINT uk_dim_product UNIQUE (product_id)
);

-- 8) Fact table: GreenCart recommendations
CREATE TABLE fact_green_recommendation (
    fact_id                 BIGINT AUTO_INCREMENT PRIMARY KEY,

    date_key                INT,
    customer_key            INT,
    loyalty_tier_key        INT,
    sust_goal_key           INT,
    channel_key             INT,
    store_key               INT NULL,
    product_orig_key        INT,
    product_alt_key         INT,

    accepted_flag           TINYINT(1),
    orig_sustainability_score INT,
    alt_sustainability_score  INT,
    sust_gain_points        INT,
    price_diff              DECIMAL(10,2),
    recommendation_score    DECIMAL(10,4),

    session_id              VARCHAR(64),

    CONSTRAINT fk_fgr_date         FOREIGN KEY (date_key)         REFERENCES dim_date(date_key),
    CONSTRAINT fk_fgr_customer     FOREIGN KEY (customer_key)     REFERENCES dim_customer(customer_key),
    CONSTRAINT fk_fgr_loyalty      FOREIGN KEY (loyalty_tier_key) REFERENCES dim_loyalty_tier(loyalty_tier_key),
    CONSTRAINT fk_fgr_sust_goal    FOREIGN KEY (sust_goal_key)    REFERENCES dim_sustainability_goal(sust_goal_key),
    CONSTRAINT fk_fgr_channel      FOREIGN KEY (channel_key)      REFERENCES dim_channel(channel_key),
    CONSTRAINT fk_fgr_store        FOREIGN KEY (store_key)        REFERENCES dim_store(store_key),
    CONSTRAINT fk_fgr_prod_orig    FOREIGN KEY (product_orig_key) REFERENCES dim_product(product_key),
    CONSTRAINT fk_fgr_prod_alt     FOREIGN KEY (product_alt_key)  REFERENCES dim_product(product_key)
);
