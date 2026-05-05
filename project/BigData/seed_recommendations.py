# see_recommendations.py

import random
import math
from datetime import datetime, timedelta
from decimal import Decimal

import pandas as pd
import mysql.connector


# ========== DB CONFIG ==========
MYSQL_USER = "root"
MYSQL_PASS = "Pari@2464"       # adjust if needed
MYSQL_HOST = "localhost"
MYSQL_DB   = "walmart_oltp"


def get_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB
    )


def acceptance_probability(sust_gain, price_diff):
    """
    Compute a probability [0,1] that a customer accepts a greener option.
    """
    sust_gain = float(sust_gain or 0.0)
    price_diff = float(price_diff or 0.0)

    score = 0.15 * sust_gain - 0.05 * max(price_diff, 0.0)
    prob = 1.0 / (1.0 + math.exp(-score / 10.0))
    return max(0.0, min(1.0, prob))


def random_datetime(start, end):
    """Random datetime between start and end."""
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)


def main():
    conn = get_connection()
    cur = conn.cursor()

    print("Loading customers/products/stores...")

    customers_df = pd.read_sql("SELECT customer_id FROM customer", conn)
    products_df = pd.read_sql("""
        SELECT 
            p.product_id,
            p.category,
            p.base_price,
            COALESCE(ps.overall_score, 50) AS overall_score
        FROM product p
        LEFT JOIN product_sustainability ps
          ON p.product_id = ps.product_id
    """, conn)

    stores_df = pd.read_sql("SELECT store_id FROM store", conn)

    customers = customers_df["customer_id"].tolist()
    stores = stores_df["store_id"].tolist()

    # Group products by category
    products_by_cat = {}
    for _, row in products_df.iterrows():
        products_by_cat.setdefault(row["category"], []).append(row)

    channels = ["STORE", "WEB", "APP"]

    n_recos = 1200
    print(f"Generating {n_recos} synthetic recommendations...")

    start_dt = datetime(2024, 1, 1)
    end_dt   = datetime(2025, 12, 31, 23, 59, 59)

    rec_rows = []
    txn_rows = []  # for transaction_header

    for i in range(n_recos):
        customer_id = random.choice(customers)
        store_id = random.choice(stores)
        channel = random.choices(channels, weights=[0.4, 0.4, 0.2])[0]

        # Pick original product
        orig = products_df.sample(1).iloc[0]
        orig_product_id = int(orig["product_id"])
        orig_score = float(orig["overall_score"])
        orig_price = float(orig["base_price"])
        orig_cat = orig["category"]

        # Pick an alt product (same category preferred)
        same_cat_products = products_by_cat.get(orig_cat, products_df.to_dict("records"))
        alt_row = random.choice(same_cat_products)
        alt_product_id = int(alt_row["product_id"])
        alt_score = float(alt_row["overall_score"])

        # Price difference
        price_diff = random.uniform(-10, 10)
        sust_gain = alt_score - orig_score

        # Acceptance model
        prob = acceptance_probability(sust_gain, price_diff)
        accepted_flag = 1 if random.random() < prob else 0

        # Timestamp & session
        decision_timestamp = random_datetime(start_dt, end_dt)
        session_id = f"SID-{i+1:06d}"

        # Add OLTP sustainable_recommendation row
        rec_rows.append((
            session_id,
            customer_id,
            orig_product_id,
            alt_product_id,
            decision_timestamp,
            accepted_flag,
            orig_score,
            alt_score,
            price_diff
        ))

        # Add OLTP transaction_header row (store + channel)
        txn_rows.append((
            session_id,
            store_id,
            channel,
            decision_timestamp
        ))

    # Insert into sustainable_recommendation
    print("Inserting recommendations into sustainable_recommendation...")

    insert_rec_sql = """
        INSERT INTO sustainable_recommendation (
            session_id,
            customer_id,
            original_product_id,
            alt_product_id,
            decision_timestamp,
            accepted_flag,
            orig_sustainability_score,
            alt_sustainability_score,
            price_diff
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cur.executemany(insert_rec_sql, rec_rows)
    conn.commit()

    print("Inserting transactions into transaction_header...")

    insert_txn_sql = """
        INSERT IGNORE INTO transaction_header (
            transaction_id_raw,
            store_id,
            channel,
            transaction_timestamp
        )
        VALUES (%s, %s, %s, %s)
    """

    cur.executemany(insert_txn_sql, txn_rows)
    conn.commit()

    print("Done! Synthetic data successfully created.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
