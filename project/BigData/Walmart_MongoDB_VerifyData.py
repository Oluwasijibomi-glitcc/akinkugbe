"""
Walmart_MongoDB_VerifyData.py

Purpose:
    Connects to the 'walmart_nosql' database and prints the document count
    for each collection to verify data ingestion was successful.
"""

from pymongo import MongoClient

# ========== CONFIGURATION ==========
MONGO_URI = "mongodb://44.200.178.89:27017/"
MONGO_DB_NAME = "walmart_nosql"

def verify_data():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[MONGO_DB_NAME]
        
        print(f"--- Verifying Database: {MONGO_DB_NAME} ---\n")

        collections_to_check = [
            "CustomerFeatures",
            "transaction_header",
            "transaction_line_item",
            "promotion",
            "promotion_eligibility",
            "customer_loyalty_profile"
        ]

        total_docs = 0
        for col_name in collections_to_check:
            count = db[col_name].count_documents({})
            print(f"Collection '{col_name}': {count:,} documents")
            total_docs += count

        print(f"\nTotal Documents: {total_docs:,}")
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

if __name__ == "__main__":
    verify_data()