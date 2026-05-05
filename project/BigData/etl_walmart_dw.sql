USE walmart_dwh;

#------------------------------------------------------------
-- 1. LOAD SMALL DIMENSIONS (CHANNEL, LOYALTY, SUST GOAL)
#------------------------------------------------------------

-- dim_channel
INSERT INTO dim_channel (channel_code, description)
SELECT *
FROM (
    SELECT 'STORE', 'In-store purchases'
    UNION ALL SELECT 'WEB',  'Web orders'
    UNION ALL SELECT 'APP',  'Mobile app orders'
) AS v(channel_code, description)
ON DUPLICATE KEY UPDATE description = v.description;


-- dim_loyalty_tier
INSERT INTO dim_loyalty_tier (loyalty_tier, description)
SELECT *
FROM (
    SELECT 'BRONZE',   'Entry-level segment'
    UNION ALL SELECT 'SILVER',   'Moderately engaged customers'
    UNION ALL SELECT 'GOLD',     'High-value customers'
    UNION ALL SELECT 'PLATINUM', 'Top-tier VIP customers'
) AS v(loyalty_tier, description)
ON DUPLICATE KEY UPDATE description = v.description;


-- dim_sustainability_goal
INSERT INTO dim_sustainability_goal (sust_goal_code, description)
SELECT *
FROM (
    SELECT 'low',    'Low sustainability emphasis'
    UNION ALL SELECT 'medium', 'Balanced sustainability & price'
    UNION ALL SELECT 'high',   'Strong sustainability orientation'
) AS v(sust_goal_code, description)
ON DUPLICATE KEY UPDATE description = v.description;




#------------------------------------------------------------
-- 2. LOAD dim_customer
#------------------------------------------------------------
INSERT INTO dim_customer (customer_id, first_name, last_name, zip_code, region)
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.zip_code,
    'GLOBAL' AS region
FROM walmart_app.customer c
ON DUPLICATE KEY UPDATE
    first_name = VALUES(first_name),
    last_name  = VALUES(last_name),
    zip_code   = VALUES(zip_code),
    region     = VALUES(region);




#-----------------------------------------------------------
-- 3. LOAD dim_store
#------------------------------------------------------------
INSERT INTO dim_store (
    store_id,
    store_name,
    store_type,
    city,
    state,
    zip_code,
    region
)
SELECT
    s.store_id,
    s.store_name,
    s.store_type,
    s.city,
    s.state,
    s.zip_code,
    s.region
FROM walmart_app.store s
ON DUPLICATE KEY UPDATE
    store_name = VALUES(store_name),
    store_type = VALUES(store_type),
    city       = VALUES(city),
    state      = VALUES(state),
    zip_code   = VALUES(zip_code),
    region     = VALUES(region);





#---------------------------------------------------------
-- 4. LOAD dim_product (with sustainability attributes)
#-----------------------------------------------------------
INSERT INTO dim_product (
    product_id,
    sku,
    product_name,
    category,
    sub_category,
    base_price,
    overall_score,
    packaging_type,
    is_local
)
SELECT
    p.product_id,
    p.sku,
    p.product_name,
    p.category,
    p.sub_category,
    p.base_price,
    ps.overall_score,
    ps.packaging_type,
    ps.is_local
FROM walmart_app.product p
LEFT JOIN walmart_app.product_sustainability ps
    ON p.product_id = ps.product_id
ON DUPLICATE KEY UPDATE
    sku            = VALUES(sku),
    product_name   = VALUES(product_name),
    category       = VALUES(category),
    sub_category   = VALUES(sub_category),
    base_price     = VALUES(base_price),
    overall_score  = VALUES(overall_score),
    packaging_type = VALUES(packaging_type),
    is_local       = VALUES(is_local);



#-----------------------------------------------------------
-- 5. FACT LOAD — fact_green_recommendation
#-----------------------------------------------------------

-- OPTIONAL CLEAN FACT TABLE
-- TRUNCATE TABLE fact_green_recommendation;


INSERT INTO fact_green_recommendation (
    date_key,
    customer_key,
    loyalty_tier_key,
    sust_goal_key,
    channel_key,
    store_key,
    product_orig_key,
    product_alt_key,
    accepted_flag,
    orig_sustainability_score,
    alt_sustainability_score,
    sust_gain_points,
    price_diff,
    recommendation_score,
    session_id
)
SELECT
    dd.date_key,

    dc.customer_key,
    dlt.loyalty_tier_key,
    dsg.sust_goal_key,

    COALESCE(dch.channel_key, 1) AS channel_key,

    ds.store_key,

    dp_orig.product_key AS product_orig_key,
    dp_alt.product_key  AS product_alt_key,

    sr.accepted_flag,
    sr.orig_sustainability_score,
    sr.alt_sustainability_score,

    (sr.alt_sustainability_score - sr.orig_sustainability_score) AS sust_gain_points,

    sr.price_diff,

    (
        csp.weight_environment *
            ((sr.alt_sustainability_score - sr.orig_sustainability_score) / 100.0)
        -
        csp.weight_price_sensitivity *
            (GREATEST(sr.price_diff, 0) /
             GREATEST(dp_orig.base_price, 1))
    ) AS recommendation_score,

    sr.session_id


FROM walmart_app.sustainable_recommendation sr

JOIN dim_date dd
    ON dd.date_key = DATE_FORMAT(sr.decision_timestamp, '%Y%m%d') + 0

JOIN walmart_app.customer c
    ON sr.customer_id = c.customer_id

JOIN walmart_app.customer_loyalty_profile clp
    ON clp.customer_id = c.customer_id

JOIN walmart_app.customer_sustainability_profile csp
    ON csp.customer_id = c.customer_id

JOIN dim_customer dc
    ON dc.customer_id = c.customer_id

JOIN dim_loyalty_tier dlt
    ON dlt.loyalty_tier = clp.loyalty_tier

JOIN dim_sustainability_goal dsg
    ON dsg.sust_goal_code = csp.overall_sustainability_goal

LEFT JOIN walmart_app.transaction_header th
    ON sr.session_id = th.transaction_id_raw

LEFT JOIN dim_channel dch
    ON dch.channel_code = th.channel

LEFT JOIN dim_store ds
    ON ds.store_id = th.store_id

JOIN dim_product dp_orig
    ON dp_orig.product_id = sr.original_product_id

JOIN dim_product dp_alt
    ON dp_alt.product_id = sr.alt_product_id;
