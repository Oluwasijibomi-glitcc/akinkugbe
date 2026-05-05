# green_insights_and_plots.py
"""
Advanced analytics & visualizations for Walmart GreenCart Data Warehouse.

This script:
  - Connects to MySQL walmart_dwh
  - Runs 12 decision-making queries
  - Prints results to console
  - Saves charts as PNGs for use in reports / slides
"""

import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# ------------- DB CONFIG -------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Pari@2464",   # adjust if needed
    "database": "walmart_dwh"
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def run_query(sql: str) -> pd.DataFrame:
    """Execute SQL and return a pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql(sql, conn)
    conn.close()
    return df


def main():
    # Make matplotlib a bit less cramped
    plt.rcParams.update({"figure.autolayout": True})

    # ---------------------------------
    # Q1 – Acceptance by Loyalty Tier
    # ---------------------------------
    sql_q1 = """
    SELECT
        dlt.loyalty_tier,
        COUNT(*) AS total_recos,
        SUM(f.accepted_flag) AS accepted_recos,
        ROUND(SUM(f.accepted_flag)/COUNT(*) * 100, 2) AS acceptance_rate_pct
    FROM fact_green_recommendation f
    JOIN dim_loyalty_tier dlt
      ON f.loyalty_tier_key = dlt.loyalty_tier_key
    GROUP BY dlt.loyalty_tier
    ORDER BY acceptance_rate_pct DESC;
    """
    df_q1 = run_query(sql_q1)
    print("\nQ1 – Acceptance by Loyalty Tier:")
    print(df_q1)

    plt.figure(figsize=(6, 4))
    plt.bar(df_q1["loyalty_tier"], df_q1["acceptance_rate_pct"])
    plt.title("Acceptance Rate by Loyalty Tier")
    plt.xlabel("Loyalty Tier")
    plt.ylabel("Acceptance Rate (%)")
    plt.savefig("q1_acceptance_by_loyalty_tier.png")
    plt.close()

    # ---------------------------------
    # Q2 – Price vs Sustainability Gain (Accepted only)
    # ---------------------------------
    sql_q2 = """
    SELECT
        dp.category,
        AVG(f.sust_gain_points) AS avg_sust_gain_points,
        AVG(f.price_diff) AS avg_price_diff,
        COUNT(*) AS accepted_count
    FROM fact_green_recommendation f
    JOIN dim_product dp
      ON f.product_alt_key = dp.product_key
    WHERE f.accepted_flag = 1
    GROUP BY dp.category
    HAVING COUNT(*) >= 20
    ORDER BY avg_sust_gain_points DESC;
    """
    df_q2 = run_query(sql_q2)
    print("\nQ2 – Price vs Sustainability Gain (Accepted Only):")
    print(df_q2)

    plt.figure(figsize=(7, 5))
    plt.scatter(df_q2["avg_price_diff"], df_q2["avg_sust_gain_points"])
    for _, row in df_q2.iterrows():
        plt.text(row["avg_price_diff"], row["avg_sust_gain_points"], row["category"], fontsize=8)
    plt.title("Price Difference vs Sustainability Gain (Accepted)")
    plt.xlabel("Avg Price Difference ($)")
    plt.ylabel("Avg Sustainability Gain (points)")
    plt.savefig("q2_price_vs_sust_gain.png")
    plt.close()

    # ---------------------------------
    # Q3 – Channel Effectiveness
    # ---------------------------------
    sql_q3 = """
    SELECT
        dch.channel_code,
        COUNT(*) AS total_recos,
        SUM(f.accepted_flag) AS accepted_recos,
        ROUND(SUM(f.accepted_flag)/COUNT(*) * 100, 2) AS acceptance_rate_pct
    FROM fact_green_recommendation f
    JOIN dim_channel dch
      ON f.channel_key = dch.channel_key
    GROUP BY dch.channel_code
    ORDER BY acceptance_rate_pct DESC;
    """
    df_q3 = run_query(sql_q3)
    print("\nQ3 – Channel Effectiveness:")
    print(df_q3)

    plt.figure(figsize=(6, 4))
    plt.bar(df_q3["channel_code"], df_q3["acceptance_rate_pct"])
    plt.title("Acceptance Rate by Channel")
    plt.xlabel("Channel")
    plt.ylabel("Acceptance Rate (%)")
    plt.savefig("q3_acceptance_by_channel.png")
    plt.close()

    # ---------------------------------
    # Q4 – Monthly Adoption Trend
    # ---------------------------------
    sql_q4 = """
    SELECT
        dd.year,
        dd.month,
        COUNT(*) AS total_recos,
        SUM(f.accepted_flag) AS accepted_recos,
        ROUND(SUM(f.accepted_flag)/COUNT(*) * 100, 2) AS acceptance_rate_pct
    FROM fact_green_recommendation f
    JOIN dim_date dd
      ON f.date_key = dd.date_key
    GROUP BY dd.year, dd.month
    ORDER BY dd.year, dd.month;
    """
    df_q4 = run_query(sql_q4)
    print("\nQ4 – Monthly Adoption Trend:")
    print(df_q4)

    df_q4["year_month"] = df_q4["year"].astype(str) + "-" + df_q4["month"].astype(str)

    plt.figure(figsize=(10, 4))
    plt.plot(df_q4["year_month"], df_q4["acceptance_rate_pct"], marker="o")
    plt.xticks(rotation=45, ha="right")
    plt.title("GreenCart Adoption Over Time")
    plt.xlabel("Year-Month")
    plt.ylabel("Acceptance Rate (%)")
    plt.savefig("q4_adoption_over_time.png")
    plt.close()

    # ---------------------------------
    # Q5 – Sustainability Goal Segmentation
    # ---------------------------------
    sql_q5 = """
    SELECT
        dsg.sust_goal_code,
        COUNT(*) AS total_recos,
        SUM(f.accepted_flag) AS accepted,
        ROUND(SUM(f.accepted_flag)/COUNT(*) * 100, 2) AS acceptance_rate
    FROM fact_green_recommendation f
    JOIN dim_sustainability_goal dsg
      ON f.sust_goal_key = dsg.sust_goal_key
    GROUP BY dsg.sust_goal_code
    ORDER BY acceptance_rate DESC;
    """
    df_q5 = run_query(sql_q5)
    print("\nQ5 – Sustainability Goal Segmentation:")
    print(df_q5)

    plt.figure(figsize=(6, 4))
    plt.bar(df_q5["sust_goal_code"], df_q5["acceptance_rate"])
    plt.title("Acceptance Rate by Sustainability Goal")
    plt.xlabel("Sustainability Goal")
    plt.ylabel("Acceptance Rate (%)")
    plt.savefig("q5_acceptance_by_sustainability_goal.png")
    plt.close()

    # ---------------------------------
    # Q6 – Category Green ROI (avg gain vs avg price)
    # ---------------------------------
    sql_q6 = """
    SELECT
        dp.category,
        AVG(f.sust_gain_points) AS avg_sust_gain,
        AVG(f.price_diff) AS avg_price_diff,
        COUNT(*) AS num_recos
    FROM fact_green_recommendation f
    JOIN dim_product dp
      ON f.product_alt_key = dp.product_key
    GROUP BY dp.category
    HAVING COUNT(*) >= 20
    ORDER BY avg_sust_gain DESC;
    """
    df_q6 = run_query(sql_q6)
    print("\nQ6 – Category Green ROI (Sustainability Gain vs Price Premium):")
    print(df_q6)

    plt.figure(figsize=(7, 5))
    plt.scatter(df_q6["avg_price_diff"], df_q6["avg_sust_gain"])
    for _, row in df_q6.iterrows():
        plt.text(row["avg_price_diff"], row["avg_sust_gain"], row["category"], fontsize=8)
    plt.title("Category Green ROI (Gain vs Price Premium)")
    plt.xlabel("Avg Price Premium ($)")
    plt.ylabel("Avg Sustainability Gain (points)")
    plt.savefig("q6_category_green_roi.png")
    plt.close()

    # ---------------------------------
    # Q7 – Price Elasticity Curve
    # ---------------------------------
    sql_q7 = """
    SELECT
        price_diff,
        ROUND(AVG(accepted_flag), 4) AS acceptance_rate
    FROM fact_green_recommendation
    GROUP BY price_diff
    ORDER BY price_diff;
    """
    df_q7 = run_query(sql_q7)
    print("\nQ7 – Price Elasticity Curve:")
    print(df_q7)

    plt.figure(figsize=(7, 4))
    plt.plot(df_q7["price_diff"], df_q7["acceptance_rate"], marker="o")
    plt.title("Price Elasticity of Green Adoption")
    plt.xlabel("Price Difference ($)")
    plt.ylabel("Acceptance Rate")
    plt.savefig("q7_price_elasticity.png")
    plt.close()

    # ---------------------------------
    # Q8 – Sustainability Gain Response Curve
    # ---------------------------------
    sql_q8 = """
    SELECT
        sust_gain_points,
        ROUND(AVG(accepted_flag), 4) AS acceptance_rate
    FROM fact_green_recommendation
    GROUP BY sust_gain_points
    ORDER BY sust_gain_points;
    """
    df_q8 = run_query(sql_q8)
    print("\nQ8 – Sustainability Gain Response Curve:")
    print(df_q8)

    plt.figure(figsize=(7, 4))
    plt.plot(df_q8["sust_gain_points"], df_q8["acceptance_rate"], marker="o")
    plt.title("Acceptance Rate vs Sustainability Gain")
    plt.xlabel("Sustainability Gain (points)")
    plt.ylabel("Acceptance Rate")
    plt.savefig("q8_sust_gain_response.png")
    plt.close()

    # ---------------------------------
    # Q9 – Store-Level Adoption
    # ---------------------------------
    sql_q9 = """
    SELECT
        ds.city,
        ds.state,
        COUNT(*) AS total_recos,
        SUM(f.accepted_flag) AS accepted,
        ROUND(SUM(f.accepted_flag)/COUNT(*) * 100, 2) AS acceptance_rate
    FROM fact_green_recommendation f
    JOIN dim_store ds
      ON f.store_key = ds.store_key
    GROUP BY ds.city, ds.state
    HAVING COUNT(*) >= 10
    ORDER BY acceptance_rate DESC;
    """
    df_q9 = run_query(sql_q9)
    print("\nQ9 – Store-Level Adoption:")
    print(df_q9)

    if not df_q9.empty:
        labels_q9 = df_q9["city"] + ", " + df_q9["state"]
        plt.figure(figsize=(10, 4))
        plt.bar(labels_q9, df_q9["acceptance_rate"])
        plt.title("Store-Level Sustainability Adoption")
        plt.xlabel("Store (City, State)")
        plt.ylabel("Acceptance Rate (%)")
        plt.xticks(rotation=45, ha="right")
        plt.savefig("q9_store_adoption.png")
        plt.close()

    # ---------------------------------
    # Q10 – Customer Lifetime GreenScore
    # ---------------------------------
    # ---------------------------------
    # Q10 – Customer Lifetime GreenScore
    # ---------------------------------
    sql_q10 = """
              SELECT dc.customer_id, \
                     MIN(dc.first_name)                        AS first_name, \
                     MIN(dc.last_name)                         AS last_name, \
                     SUM(f.sust_gain_points * f.accepted_flag) AS lifetime_green_points, \
                     SUM(f.accepted_flag)                      AS accepted_recos
              FROM fact_green_recommendation f
                       JOIN dim_customer dc
                            ON f.customer_key = dc.customer_key
              GROUP BY dc.customer_id
              ORDER BY lifetime_green_points DESC
              LIMIT 50; \
              """

    df_q10 = run_query(sql_q10)
    print("\nQ10 – Customer Lifetime GreenScore:")
    print(df_q10)

    if not df_q10.empty:
        plt.figure(figsize=(10, 4))
        df_q10["customer_name"] = df_q10["first_name"].fillna("") + " " + df_q10["last_name"].fillna("")
        top10 = df_q10.head(10)
        plt.bar(top10["customer_name"], top10["lifetime_green_points"])
        plt.title("Top 10 Customers by Lifetime GreenScore")
        plt.xlabel("Customer")
        plt.ylabel("Lifetime Green Points")
        plt.xticks(rotation=45, ha="right")
        plt.savefig("q10_lifetime_greenscore.png")
        plt.close()

    # ---------------------------------
    # Q11 – Sustainability & Carbon by Loyalty Tier
    # ---------------------------------
    sql_q11 = """
              SELECT dlt.loyalty_tier, \
                     AVG(dp_alt.overall_score) AS avg_sustainability_score, \
                     COUNT(*)                  AS num_recommendations
              FROM fact_green_recommendation f
                       JOIN dim_loyalty_tier dlt
                            ON f.loyalty_tier_key = dlt.loyalty_tier_key
                       JOIN dim_product dp_alt
                            ON f.product_alt_key = dp_alt.product_key
              GROUP BY dlt.loyalty_tier
              ORDER BY avg_sustainability_score DESC; \
              """
    df_q11 = run_query(sql_q11)
    print("\nQ11 – Sustainability & Carbon by Loyalty Tier:")
    print(df_q11)

    plt.figure(figsize=(6, 4))
    plt.bar(df_q11["loyalty_tier"], df_q11["avg_sustainability_score"])
    plt.title("Average Sustainability Score by Loyalty Tier")
    plt.xlabel("Loyalty Tier")
    plt.ylabel("Avg Sustainability Score")
    plt.savefig("q11_sustainability_by_loyalty.png")
    plt.close()

    # ---------------------------------
    # Q12 – Category Carbon Impact
    # ---------------------------------
    sql_q12 = """
              SELECT dp.category, \
                     AVG(dp.overall_score) AS avg_sustainability_score, \
                     COUNT(*)              AS num_alt_products, \
                     AVG(dp.base_price)    AS avg_alt_price
              FROM fact_green_recommendation f
                       JOIN dim_product dp
                            ON f.product_alt_key = dp.product_key
              GROUP BY dp.category
              ORDER BY avg_sustainability_score DESC; \
              """

    df_q12 = run_query(sql_q12)
    print("\nQ12 – Category Carbon Impact:")
    print(df_q12)

    plt.figure(figsize=(10, 4))
    plt.bar(df_q12["category"], df_q12["avg_sustainability_score"])
    plt.title("Average Sustainability Score by Category")
    plt.xlabel("Category")
    plt.ylabel("Avg Sustainability Score")
    plt.xticks(rotation=45, ha="right")
    plt.savefig("q12_sustainability_by_category.png")
    plt.close()

    print("\n All queries executed and charts saved.")


if __name__ == "__main__":
    main()
