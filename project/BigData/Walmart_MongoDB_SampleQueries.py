"""
Walmart_MongoDB_SampleQueries.py
Purpose:
    Demonstrates how to query the Walmart NoSQL database (MongoDB) using Python.
"""

from pymongo import MongoClient
import pprint

# ========== CONFIGURATION ==========
MONGO_URI = "mongodb://44.200.178.89:27017/"
MONGO_DB_NAME = "walmart_nosql"

class WalmartQueryTool:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.pp = pprint.PrettyPrinter(indent=2)

    def find_customer_by_id(self, customer_id):
        """Find a specific customer's profile."""
        print(f"\n--- Searching for Customer ID: {customer_id} ---")
        doc = self.db.CustomerFeatures.find_one({"customer_id": customer_id})
        if doc:
            self.pp.pprint(doc)
        else:
            print("Customer not found.")

    def find_customers_by_tier(self, tier, limit=5):
        """Find customers in a specific loyalty tier."""
        print(f"\n--- First {limit} {tier} Customers ---")
        # Use 'loyalty_tier' from the merged profile data
        cursor = self.db.CustomerFeatures.find({"loyalty_tier": tier}).sort("TotalSpend", -1).limit(limit)
        for doc in cursor:
            print(f"ID: {doc.get('customer_id')} | Spend: ${doc.get('TotalSpend'):.2f} | Points: {doc.get('points_balance')}")

    def analyze_loyalty_points(self):
        """Aggregation: Average points per tier."""
        print("\n--- Average Loyalty Points by Tier ---")
        pipeline = [
            {"$group": {"_id": "$loyalty_tier", "avg_points": {"$avg": "$points_balance"}, "count": {"$sum": 1}}},
            {"$sort": {"avg_points": -1}}
        ]
        results = self.db.CustomerFeatures.aggregate(pipeline)
        print(f"{'Tier':<15} | {'Count':<10} | {'Avg Points':<15}")
        print("-" * 45)
        for r in results:
            if r['_id']:
                print(f"{r['_id']:<15} | {r['count']:<10} | {r['avg_points']:.2f}")

    def check_customer_eligibility(self, customer_id):
        """Check which promotions a specific customer is eligible for."""
        print(f"\n--- Checking Eligibility for Customer: {customer_id} ---")
        eligibility_cursor = self.db.promotion_eligibility.find({"customer_id": customer_id})
        
        found = False
        for elig in eligibility_cursor:
            found = True
            promo_id = elig.get('promo_id')
            promo_details = self.db.promotion.find_one({"promo_id": promo_id})
            
            if promo_details:
                print(f"✅ Eligible for: {promo_details['promo_name']} (Reason: {elig.get('eligibility_reason')})")
            else:
                print(f"⚠️ Eligible for Promo ID {promo_id}, but details not found.")
        
        if not found:
            print("No active promotion eligibility found for this customer.")

# ========== MAIN EXECUTION ==========
def main():
    tool = WalmartQueryTool()

    # 1. Summaries
    tool.analyze_loyalty_points()
    tool.find_customers_by_tier("GOLD", limit=3)

    # 2. Check a sample customer
    sample = tool.db.CustomerFeatures.find_one({"loyalty_tier": "PLATINUM"})
    if sample:
        tool.find_customer_by_id(sample['customer_id'])
        tool.check_customer_eligibility(sample['customer_id'])

if __name__ == "__main__":
    main()