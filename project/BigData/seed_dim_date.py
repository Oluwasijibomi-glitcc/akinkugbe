# seed_dim_date.py

import mysql.connector
from datetime import date, timedelta

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Pari@2464",  # change if needed
    "database": "walmart_dwh"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def seed_dim_date(start_date, end_date):
    conn = get_connection()
    cur = conn.cursor()

    current = start_date
    rows = []

    while current <= end_date:
        date_key = int(current.strftime("%Y%m%d"))
        year = current.year
        quarter = (current.month - 1) // 3 + 1
        month = current.month
        month_name = current.strftime("%B")
        day = current.day
        day_name = current.strftime("%A")
        week_of_year = int(current.strftime("%U"))

        rows.append((
            date_key,
            current,
            year,
            quarter,
            month,
            month_name,
            day,
            day_name,
            week_of_year
        ))

        current += timedelta(days=1)

    sql = """
    INSERT INTO dim_date
    (date_key, full_date, year, quarter, month, month_name, day, day_name, week_of_year)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        full_date = VALUES(full_date),
        year = VALUES(year),
        quarter = VALUES(quarter),
        month = VALUES(month),
        month_name = VALUES(month_name),
        day = VALUES(day),
        day_name = VALUES(day_name),
        week_of_year = VALUES(week_of_year)
    """
    cur.executemany(sql, rows)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted/updated {len(rows)} dim_date rows")

if __name__ == "__main__":
    start = date(2023, 1, 1)
    end   = date(2027, 12, 31)
    seed_dim_date(start, end)
