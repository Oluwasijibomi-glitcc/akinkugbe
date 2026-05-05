"""
Walmart_MongoDB.py

ETL Script: S3 CSVs -> MongoDB (Raw Data & Customer Features)

Purpose:
    1. Ingests raw CSVs from S3 (Transactions, Promotions, Loyalty) into MongoDB.
    2. Builds 'CustomerFeatures' collection by aggregating transactions and 
       merging with loyalty profile data.

Prerequisites:
    - AWS S3 Bucket (MUST be accessible by your Lab User).
    - MongoDB instance.
    - AWS Credentials (Access Key, Secret Key, AND Session Token for Labs).
"""

import pandas as pd
import boto3
import io
import sys
from pymongo import MongoClient, errors

# ========== CONFIGURATION ==========

# 1. AWS S3 Configuration
AWS_REGION = "us-east-1"

# !!! CRITICAL: UPDATE THIS TO YOUR ACTUAL BUCKET NAME !!!
S3_BUCKET_NAME = "project-bucket-0444"  

# Files to Ingest
FILE_KEY_HEADER = "data/transaction_header.csv"
FILE_KEY_LINE_ITEM = "data/transaction_line_item.csv"
FILE_KEY_PROMOTION = "data/promotion.csv"
FILE_KEY_ELIGIBILITY = "data/promotion_eligibility.csv"
FILE_KEY_LOYALTY = "data/customer_loyalty_profile.csv"

# 2. AWS CREDENTIALS (REQUIRED FOR LABS)
AWS_ACCESS_KEY_ID = "ASIA4MTWI2SYDMAI6ETD"
AWS_SECRET_ACCESS_KEY = "hbqIVmkun3XwhxGq9KNcnwyPrM1dnj7cahsnRzAH"
AWS_SESSION_TOKEN = "IQoJb3JpZ2luX2VjEIz//////////wEaCXVzLXdlc3QtMiJIMEYCIQDSDuVLTqVNJRQWgNyXwRjDv0INpHjqPbHWUcfBLwo3UQIhAMnH1gRY3FXhyb6nZgqmfhjTm8wKBZHQ3g9BeYGOkGeeKqsCCFUQARoMODUxNzI1MzA5MTA0Igx+HiqcleEXWVQRFXsqiAKmEugtuUDZ6BUFbZQYoYq51qefHvJApxAksZQAWungDM3HDBSrf8CsrWpuO5LB0nuMMhrnqs9PQE+tSfk7pmXtli2BmiqzFoK3U5hsZGXUq4bKrw4hjh6kU3DSOvgiiezO4aTeafa0MvPBhDJk/2FIUe0cP+ztaTyeXrWJX7520mJ0fGF6wVO3Mt4q+hckVDB++7PLXJUqJPXaqfhw0oTvgY1p0YbXhhjyf8FgIhFNJSIr0s+YYwOSbHkRMYsJYuWvU+I6SRKJ87j4M7wo38/eabPuuGuXIIhu0QAaMd0zh3eRfCmpfqPvyX3oajEgudXsgXZJvGmzoSQHP65bfofjKbXy5mh+clswrq/JyQY6nAHjSia4kZtrfdgJ4f0zgdjhYr6iKqtFaKpgkEahAF4kWMHtVEo+eNNJvkd1Ha65cUoYkNeTUtel0JBdEu1PtaHkmFrgECQa3pDD/cNGqCMWIZT9gnvi+oAZcvb7pklGJqB1woorJPFy69/es4ogoOLDemd5tyEwWTMWTU2op6E+wEloH6Nqnmiov3XfPudfc/JjYo5/JCrBjWj/AaU="

# 3. MongoDB Configuration
MONGO_URI = "mongodb://44.200.178.89:27017/"
MONGO_DB_NAME = "walmart_nosql"


# ========== S3 CONNECTION ==========
def get_s3_client():
    """
    Creates boto3 client with explicit Lab credentials.
    """
    if AWS_ACCESS_KEY_ID != "YOUR_ACCESS_KEY":
        return boto3.client(
            's3',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_session_token=AWS_SESSION_TOKEN
        )
    else:
        print("Using environment credentials...")
        return boto3.client('s3', region_name=AWS_REGION)


def read_csv_from_s3(s3_client, bucket, key):
    print(f"Reading {key} from bucket {bucket}...")
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        return pd.read_csv(io.BytesIO(obj['Body'].read()))
    except Exception as e:
        print(f"Error reading {key}: {e}")
        return None


# ========== MONGODB CONNECTION ==========
def get_mongo_collection(collection_name):
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB_NAME]
    return db[collection_name]

def test_mongo_connection():
    print(f"Testing connection to MongoDB at: {MONGO_URI} ...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ismaster')
        print("✅ MongoDB connection successful!\n")
    except errors.ServerSelectionTimeoutError:
        print("\n❌ CONNECTION FAILED: Could not reach MongoDB.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ CONNECTION FAILED: {e}")
        sys.exit(1)


# ========== DATA INGESTION UTILS ==========
def ingest_raw_file(s3_client, s3_key, collection_name):
    print(f"\n--- Ingesting {s3_key} into {collection_name} ---")
    df = read_csv_from_s3(s3_client, S3_BUCKET_NAME, s3_key)
    
    if df is not None:
        records = df.to_dict("records")
        if records:
            col = get_mongo_collection(collection_name)
            col.delete_many({}) # Clear existing data
            col.insert_many(records)
            print(f"Successfully inserted {len(records)} documents into '{collection_name}'.")
        else:
            print("DataFrame was empty, no data inserted.")
    else:
        print(f"Skipping {collection_name} due to read error.")


# ========== BUILD CUSTOMER FEATURES (TRANSFORMATION LOGIC) ==========
def build_customer_features(s3_client):
    print("\n--- Building Customer Features ---")
    
    # 1. Load Transaction Data
    df_header = read_csv_from_s3(s3_client, S3_BUCKET_NAME, FILE_KEY_HEADER)
    df_line = read_csv_from_s3(s3_client, S3_BUCKET_NAME, FILE_KEY_LINE_ITEM)
    
    # 2. Load Loyalty Data
    df_loyalty = read_csv_from_s3(s3_client, S3_BUCKET_NAME, FILE_KEY_LOYALTY)

    if df_header is None or df_line is None:
        print("Cannot build features: Missing source files.")
        return None

    # 3. Aggregate Transactions
    merged_df = pd.merge(df_header, df_line, on='transaction_id', how='inner')
    merged_df['line_total'] = merged_df['quantity'] * merged_df['unit_price']

    features_df = merged_df.groupby('customer_id').agg(
        NumOrders=('transaction_id', 'nunique'),
        TotalSpend=('line_total', 'sum'),
        LastPurchaseDate=('transaction_timestamp', 'max')
    ).reset_index()

    # 4. Merge with Loyalty Data
    if df_loyalty is not None:
        print("Merging transaction data with loyalty profile...")
        # Left join to keep all transaction customers, add loyalty info where matches
        features_df = pd.merge(features_df, df_loyalty, on='customer_id', how='left')
    
    # Fill NaN for customers missing loyalty profiles
    features_df["points_balance"] = features_df["points_balance"].fillna(0)
    features_df["loyalty_tier"] = features_df["loyalty_tier"].fillna("UNREGISTERED")

    # 5. Final Formatting
    features_df["LastPurchaseDate"] = features_df["LastPurchaseDate"].astype(str)
    
    return features_df


# ========== MAIN EXECUTION ==========
def main():
    test_mongo_connection()
    s3 = get_s3_client()
    print(f"Target Bucket: {S3_BUCKET_NAME}")
    
    # 1. Ingest Raw Files
    ingest_raw_file(s3, FILE_KEY_HEADER, "transaction_header")
    ingest_raw_file(s3, FILE_KEY_LINE_ITEM, "transaction_line_item")
    ingest_raw_file(s3, FILE_KEY_PROMOTION, "promotion")
    ingest_raw_file(s3, FILE_KEY_ELIGIBILITY, "promotion_eligibility")
    ingest_raw_file(s3, FILE_KEY_LOYALTY, "customer_loyalty_profile")

    # 2. Build Customer Features
    try:
        features_df = build_customer_features(s3)
        if features_df is not None:
            col = get_mongo_collection("CustomerFeatures")
            col.delete_many({})
            records = features_df.to_dict("records")
            if records:
                col.insert_many(records)
            print(f"Inserted {len(records)} documents into 'CustomerFeatures'.")
              
    except Exception as e:
        print(f"An error occurred during feature building: {e}")


if __name__ == "__main__":
    main()