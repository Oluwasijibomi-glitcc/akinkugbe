import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime

# ================== DB CONFIG ==================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Pari@2464",   # change if needed
    "database": "walmart_oltp"
}

# ================== SESSION STATE INIT ==================
if "chosen_alt_pid" not in st.session_state:
    st.session_state.chosen_alt_pid = None

if "recs_df" not in st.session_state:
    st.session_state.recs_df = None

# ================== DB UTILITIES ==================
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

def load_customers():
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    try:
        df = pd.read_sql("""
            SELECT c.customer_id,
                   CONCAT(c.first_name, ' ', c.last_name) AS customer_name
            FROM customer c
            ORDER BY c.customer_id
        """, conn)
        return df
    finally:
        conn.close()

def load_products():
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    try:
        df = pd.read_sql("""
            SELECT p.product_id,
                   p.product_name,
                   p.category,
                   p.base_price
            FROM product p
            WHERE p.is_active = 1
            ORDER BY p.product_name
        """, conn)
        return df
    finally:
        conn.close()

def get_recommendations(customer_id, orig_product_id, max_price_increase_pct=0.25):
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    try:
        query = """
        SELECT
            alt.product_id,
            alt.product_name,
            alt.category,
            alt.sub_category,
            alt.base_price AS alt_price,
            orig.base_price AS orig_price,
            ps_orig.overall_score AS orig_sust_score,
            ps_alt.overall_score AS alt_sust_score,
            (ps_alt.overall_score - ps_orig.overall_score) AS sust_gain_points,
            (ps_alt.overall_score - ps_orig.overall_score) / 100.0 AS sust_gain_norm,
            (alt.base_price - orig.base_price) AS price_diff,
            GREATEST(alt.base_price - orig.base_price, 0) / GREATEST(orig.base_price, 1) AS price_penalty_norm,
            csp.weight_environment AS w_env,
            csp.weight_price_sensitivity AS w_price,
            (
                csp.weight_environment *
                    ((ps_alt.overall_score - ps_orig.overall_score) / 100.0)
                -
                csp.weight_price_sensitivity *
                    (GREATEST(alt.base_price - orig.base_price, 0) /
                     GREATEST(orig.base_price, 1))
            ) AS recommendation_score
        FROM customer_sustainability_profile csp
        JOIN product orig
            ON orig.product_id = %(orig_pid)s
        JOIN product_sustainability ps_orig
            ON ps_orig.product_id = orig.product_id
        JOIN product alt
            ON alt.category = orig.category
            AND alt.product_id <> orig.product_id
            AND alt.is_active = 1
        JOIN product_sustainability ps_alt
            ON ps_alt.product_id = alt.product_id
        WHERE csp.customer_id = %(cust_id)s
          AND ps_alt.overall_score > ps_orig.overall_score
          AND alt.base_price <= orig.base_price * (1 + %(max_inc)s)
        ORDER BY recommendation_score DESC
        LIMIT 20;
        """
        params = {
            "cust_id": customer_id,
            "orig_pid": orig_product_id,
            "max_inc": max_price_increase_pct
        }
        df = pd.read_sql(query, conn, params=params)
        return df
    finally:
        conn.close()

def log_recommendation(customer_id, session_id, orig_pid, alt_pid,
                       orig_score, alt_score, price_diff, accepted_flag):
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sustainable_recommendation
            (customer_id, session_id, original_product_id, alt_product_id,
             orig_sustainability_score, alt_sustainability_score,
             price_diff, accepted_flag, decision_timestamp)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            customer_id,
            session_id,
            orig_pid,
            alt_pid,
            orig_score,
            alt_score,
            price_diff,
            1 if accepted_flag else 0,
            datetime.now()
        ))
        conn.commit()
    except Error as e:
        st.error(f"Error logging recommendation: {e}")
    finally:
        cur.close()
        conn.close()


# ================== STREAMLIT UI ==================
st.set_page_config(page_title="Walmart GreenCart Assistant", layout="wide")

st.title("🛒 Walmart GreenCart Assistant")
st.caption("Sustainable product recommendations using customer preferences + product sustainability scores.")

# Load dropdown data
customers_df = load_customers()
products_df = load_products()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Step 1: Select Customer")
    customer_map = {
        f"{row.customer_id} - {row.customer_name}": row.customer_id
        for _, row in customers_df.iterrows()
    }
    customer_label = st.selectbox("Customer", list(customer_map.keys()))
    selected_customer_id = customer_map[customer_label]

with col2:
    st.subheader("Step 2: Select Product in Cart")
    product_map = {
        f"{row.product_id} - {row.product_name} (${row.base_price:.2f})": row.product_id
        for _, row in products_df.iterrows()
    }
    product_label = st.selectbox("Original Product", list(product_map.keys()))
    selected_product_id = product_map[product_label]


st.markdown("---")

st.subheader("Step 3: Recommended Greener Alternatives")

max_price_pct = st.slider(
    "Maximum allowed price increase (%)",
    min_value=0, max_value=100, value=25, step=5
) / 100.0

# === FETCH RECOMMENDATIONS ===
if st.button("Find Recommendations"):
    st.session_state.recs_df = get_recommendations(
        selected_customer_id,
        selected_product_id,
        max_price_increase_pct=max_price_pct
    )
    if st.session_state.recs_df.empty:
        st.warning("No greener alternatives found.")
    else:
        st.success("Recommendations loaded!")

# === DISPLAY RECOMMENDATIONS ===
if st.session_state.recs_df is not None and not st.session_state.recs_df.empty:

    recs_df = st.session_state.recs_df

    display_cols = [
        "product_id", "product_name", "category",
        "orig_price", "alt_price",
        "orig_sust_score", "alt_sust_score",
        "sust_gain_points", "price_diff",
        "recommendation_score"
    ]
    st.dataframe(recs_df[display_cols])

    st.markdown("### Log a Decision")
    session_id = st.text_input("Session / Cart ID", value="demo-session-001")

    # ---- ALTERNATIVE DROPDOWN (STATE SAFE) ----
    options = {
        f"{row.product_id} - {row.product_name}": int(row.product_id)
        for _, row in recs_df.iterrows()
    }

    selected_option = st.selectbox(
        "Choose alternative:",
        list(options.keys()),
        key="alternative_selector"
    )

    # Persist selection
    st.session_state.chosen_alt_pid = options[selected_option]

    chosen_pid = st.session_state.chosen_alt_pid
    chosen_row = recs_df.loc[recs_df["product_id"] == chosen_pid].iloc[0]

    col_a, col_b = st.columns(2)

    # ===== ACCEPT PRODUCT =====
    with col_a:
        if st.button("✅ Accept Alternative"):
            log_recommendation(
                selected_customer_id,
                session_id,
                selected_product_id,
                chosen_pid,
                float(chosen_row["orig_sust_score"]),
                float(chosen_row["alt_sust_score"]),
                float(chosen_row["price_diff"]),
                accepted_flag=True
            )
            st.success("Accepted recommendation logged.")
            st.toast("🛒 Added to cart!", icon="🛍️")

    # ===== REJECT PRODUCT =====
    with col_b:
        if st.button("❌ Reject Alternative"):
            log_recommendation(
                selected_customer_id,
                session_id,
                selected_product_id,
                chosen_pid,
                float(chosen_row["orig_sust_score"]),
                float(chosen_row["alt_sust_score"]),
                float(chosen_row["price_diff"]),
                accepted_flag=False
            )
            st.info("Recommendation rejected.")
