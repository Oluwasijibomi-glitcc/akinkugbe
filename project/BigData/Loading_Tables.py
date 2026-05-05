"""
End-to-end ETL: UCI Online Retail II -> Walmart-style OLTP CSVs

Tables produced (all as CSVs in OUTPUT_DIR):
- customer.csv
- product.csv
- store.csv
- transaction_header.csv
- transaction_line_item.csv
- payment_method.csv
- promotion.csv
- promotion_eligibility.csv
- inventory_snapshot.csv
- customer_loyalty_profile.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import random
from faker import Faker

# ========= CONFIG =========
RAW_FILE = Path(r"/Users/oluwasijibomiakinkugbe/Desktop/Managing Big Data /Project/online_retail_II 1.xlsx")
OUTPUT_DIR = Path(r"/Users/oluwasijibomiakinkugbe/Desktop/Managing Big Data /Project/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Reproducibility
random.seed(42)
np.random.seed(42)
Faker.seed(42)
fake = Faker()

# ========= LOAD RAW DATA (ALL SHEETS) =========
sheets_dict = pd.read_excel(RAW_FILE, sheet_name=None)
df = pd.concat(sheets_dict.values(), ignore_index=True)

# UCI Online Retail II column assumptions:
# Invoice, InvoiceDate, Customer ID, StockCode, Description, Quantity, Price, Country

# Basic cleaning - drop rows without essential keys
df = df.dropna(subset=["Customer ID", "StockCode"])

# Normalize/rename columns and types
df["CustomerID"] = df["Customer ID"].astype(int)
df["InvoiceNo"] = df["Invoice"].astype(str)
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["Quantity"] = df["Quantity"].astype(int)
df["UnitPrice"] = df["Price"].astype(float)

# ========= CUSTOMER TABLE =========
customers = (
    df[["CustomerID", "Country"]]
    .drop_duplicates()
    .rename(columns={
        "CustomerID": "customer_id",
        "Country": "country"
    })
)

# Generate synthetic names, emails, zip codes
first_names = []
last_names = []
emails = []
zip_codes = []

for _ in range(len(customers)):
    first = fake.first_name()
    last = fake.last_name()
    zip_code = fake.postcode()
    email = f"{first}.{last}".lower().replace(" ", "") + "@example.com"

    first_names.append(first)
    last_names.append(last)
    emails.append(email)
    zip_codes.append(zip_code)

customers["first_name"] = first_names
customers["last_name"] = last_names
customers["email"] = emails
customers["zip_code"] = zip_codes

# Initial loyalty_tier will be overwritten later from customer_loyalty_profile
customers["loyalty_tier"] = "BRONZE"
customers["date_joined"] = pd.to_datetime("2018-01-01")
customers["channel_signup"] = "WEB"

customer_cols = [
    "customer_id", "first_name", "last_name", "email",
    "zip_code", "loyalty_tier", "date_joined", "channel_signup"
]
customers = customers[customer_cols]

# ========= PRODUCT TABLE + CATEGORY CLASSIFIER =========
products = (
    df[["StockCode", "Description", "UnitPrice"]]
    .drop_duplicates(subset=["StockCode"])
    .rename(columns={
        "StockCode": "sku",
        "Description": "product_name",
        "UnitPrice": "base_price"
    })
)

products = products.reset_index(drop=True)
products["product_id"] = products.index + 1
products["category"] = None
products["sub_category"] = None
products["brand"] = None
products["is_active"] = 1

def classify_product_category(name: str):
    """
    Map product_name to (category, sub_category).
    Falls back to ('Other', 'Other') when nothing matches.
    """
    if not isinstance(name, str):
        return ("Other", "Other")
    n = name.upper().strip()

    # -------- Seasonal / Holidays --------
    if any(k in n for k in [
        "CHRISTMAS", "XMAS", "NOEL", "ADVENT", "SNOWMAN", "SANTA",
        "REINDEER", "TURKEY", "BAUBLE", "MISTLETOE", "WREATH",
        "EASTER", "VALENTINE", "SKULL", "HALLOWEEN"
    ]):
        if "LIGHT" in n or "NIGHT LIGHT" in n or "PORTABLE TABLE LIGHT" in n:
            return ("Seasonal & Celebration", "Holiday Lights & Illuminations")
        if any(k in n for k in [
            "TREE", "BAUBLE", "DECORATION", "HANGING", "GARLAND",
            "T-LIGHT", "TEALIGHT", "PAPER CHAIN"
        ]):
            return ("Seasonal & Celebration", "Holiday Decorations")
        if any(k in n for k in [
            "WRAP", "GIFT BAG", "GIFTBAG", "CARD", "TAG", "STICKER",
            "PAPER CUPS", "NAPKINS", "BUNTING"
        ]):
            return ("Seasonal & Celebration", "Holiday Partyware & Wrap")
        if "EGG" in n:
            return ("Seasonal & Celebration", "Easter Gifts & Decor")
        return ("Seasonal & Celebration", "Holiday General")

    # -------- Candles, fragrance & lighting --------
    if any(k in n for k in [
        "CANDLE", "T-LIGHT", "TEALIGHT", "T LIGHT", "LANTERN",
        "NIGHT LIGHT", "NIGHTLIGHT", "INCENSE"
    ]):
        if any(k in n for k in ["HOLDER", "POT", "JAR", "BUCKET", "LANTERN", "CADDY"]):
            return ("Home & Living", "Candle & Fragrance Holders")
        if "SET" in n:
            return ("Home & Living", "Candle & Fragrance Sets")
        return ("Home & Living", "Candles & Home Fragrance")

    # -------- Kitchen & Dining: tableware / bakeware / textiles --------
    if any(k in n for k in [
        "MUG", "MUGS", "CUP", "CUPS", "PLATE", "BOWL", "BOWLS", "TRAY",
        "CAKE STAND", "CAKE PLATE", "JUG", "PITCHER", "SAUCER",
        "DINNER PLATE", "SUNDAE DISH", "GLASS SUNDAE",
        "SALT AND PEPPER", "TEAPOT", "TEA POT", "TEA STRAINER",
        "CAKE TIN"
    ]):
        if any(k in n for k in ["MUG", "CUP", "TEA", "COFFEE", "SUNDAE"]):
            return ("Kitchen & Dining", "Drinkware & Dessertware")
        if any(k in n for k in ["PLATE", "BOWL", "TRAY", "STAND", "FORK", "CUTLERY", "CAKE", "SAUCER"]):
            return ("Kitchen & Dining", "Serveware & Tableware")
        return ("Kitchen & Dining", "General Tableware")

    if any(k in n for k in [
        "TEA TOWEL", "TEATOWEL", "TEATOWELS", "TABLE CLOTH",
        "TABLECLOTH", "NAPKIN", "NAPKINS", "DOILY", "DOILIES"
    ]):
        return ("Kitchen & Dining", "Table Linens")

    if any(k in n for k in ["COASTER", "COASTERS", "PLACEMAT", "PLACE MAT"]):
        return ("Kitchen & Dining", "Table Protection")

    if any(k in n for k in [
        "BAKING MOULD", "BISCUIT CUTTER", "COOKIE CUTTER",
        "MEASURING SPOON", "MEASURING JUG", "ROLLING PIN"
    ]):
        return ("Kitchen & Dining", "Baking Tools & Moulds")

    if any(k in n for k in ["FOOD COVER", "CAKE COVER", "CUPCAKE CASES", "FOOD COVERS"]):
        return ("Kitchen & Dining", "Food Covers & Accessories")

    if any(k in n for k in ["LUNCHBOX", "LUNCH BOX", "LUNCH BAG", "SNACK BOX"]):
        return ("Kitchen & Dining", "Food Storage & Lunchboxes")

    if any(k in n for k in ["APRONS", "APRON", "OVEN GLOVE", "OVEN GLOVES", "POT HOLDER"]):
        return ("Kitchen & Dining", "Aprons & Oven Gloves")

    # -------- Storage, tins, containers --------
    if any(k in n for k in [
        "TOTE BAG", "SHOPPER", "BAG ", " BAG", "BASKET", "BOX",
        "TRINKET", "TIN", "TINS", "JAR", "SUITCASE",
        "BREAD BIN", "BREADBOX", "CADDY", "STORAGE",
        "ORGANISER TIN", "HANDY TIN"
    ]):
        if any(k in n for k in ["TOTE BAG", "SHOPPER", "BAG ", "BAG,", "BAG-", "BAG/", "PURSE", "WALLET"]):
            return ("Fashion & Accessories", "Bags, Purses & Wallets")
        if any(k in n for k in ["TEA CADDY", "SUGAR", "BREAD", "BISCUIT", "CAKE TIN"]):
            return ("Kitchen & Dining", "Kitchen Storage Tins")
        if any(k in n for k in ["TRINKET", "HANDY TIN", "TIN ", "TINS", "SUITCASE"]):
            return ("Home & Living", "Storage Boxes & Tins")
        return ("Home & Living", "General Storage & Containers")

    # -------- Jewellery & personal accessories --------
    if any(k in n for k in ["NECKLACE", "BRACELET", "EARRING", "RING ", "ANKLET", "JEWELLERY", "JEWELRY"]):
        return ("Fashion & Accessories", "Jewellery")

    if any(k in n for k in [
        "COMPACT MIRROR", "COMPACT ", "KEYRING", "KEY RING", "KEYCHAIN",
        "KEY CHAIN", "PHONE CHARM", "PHONE STRAP"
    ]):
        return ("Fashion & Accessories", "Small Accessories & Charms")

    if any(k in n for k in ["COSMETIC BAG", "MAKE UP BAG", "MAKE-UP BAG", "WASH BAG", "BATH BAG"]):
        return ("Fashion & Accessories", "Cosmetic & Wash Bags")

    if any(k in n for k in ["HAIR BAND", "HAIRBAND", "HAIR CLIP", "HAIR ACCESSORY"]):
        return ("Fashion & Accessories", "Hair Accessories")

    # -------- Home decor & soft furnishings --------
    if any(k in n for k in [
        "FRAME", "PHOTO", "PICTURE", "POSTER", "CANVAS",
        "WALL ART", "BLACKBOARD", "CHALKBOARD"
    ]):
        return ("Home Decor", "Frames, Art & Boards")

    if any(k in n for k in ["CUSHION", "PILLOW", "THROW", "BLANKET", "HOT WATER BOTTLE"]):
        return ("Home Decor", "Cushions, Throws & Hot Water Bottles")

    if any(k in n for k in ["DOORSTOP", "DOOR STOP", "RUG", "MAT ", "DOOR MAT", "DOORMAT"]):
        return ("Home Decor", "Rugs, Mats & Doorstops")

    if any(k in n for k in [
        "VASE", "ORNAMENT", "FIGURE", "FIGURINE", "SCULPTURE",
        "DECORATION", "BIRDFEEDER", "BIRD FEEDER", "TRELLIS"
    ]):
        return ("Home Decor", "Ornaments & Decorative Objects")

    if any(k in n for k in ["SIGN", "PLAQUE", "BLOCK WORD", "LETTER", "LETTERS", "WORDS", "WORD "]):
        return ("Home Decor", "Signs & Typography")

    if any(k in n for k in ["COAT RACK", "PEG HANGER", "HOOKS", "PEG RACK"]):
        return ("Home Decor", "Hooks & Racks")

    # -------- Stationery, cards & wrap --------
    if any(k in n for k in ["NOTEBOOK", "JOURNAL", "DIARY", "ADDRESS BOOK", "SKETCHBOOK"]):
        return ("Stationery", "Notebooks & Journals")

    if any(k in n for k in ["PENCIL", "PENCILS", "PEN ", "PENS", "ERASER", "RUBBER", "SHARPENER", "STAPLER"]):
        return ("Stationery", "Writing Instruments & Accessories")

    if any(k in n for k in ["CARD", "POSTCARD", "INVITATION", "THANK YOU", "THANKYOU"]):
        return ("Stationery", "Cards & Postcards")

    if any(k in n for k in ["WRAP", "WRAPPING PAPER", "GIFT BAG", "GIFTBAG", "TISSUE", "RIBBON", "STICKER", "TAG", "TAPE", "PAPER CHAIN"]):
        return ("Stationery", "Gift Wrap & Packaging")

    if any(k in n for k in ["MAGNET", "MAGNETS", "FRIDGE MAGNET"]):
        return ("Home & Office", "Fridge Magnets & Small Gifts")

    if any(k in n for k in ["TO DO LIST", "TO-DO LIST", "LISTPAD", "LIST PAD"]):
        return ("Stationery", "Notepads & Lists")

    # -------- Toys, crafts, kids & novelty --------
    if any(k in n for k in [
        "TOY", "PUZZLE", "GAME", "YOYO", "YO-YO", "JIGSAW", "DOLL",
        "SKIPPING", "BALLOON", "BALL ", "BALLS", "TOP ",
        "BUBBLE", "KITE", "MASK", "WHISTLE", "SLINKY", "MARACAS",
        "DINOSAUR SET"
    ]):
        return ("Toys & Games", "Children's Toys & Games")

    if any(k in n for k in [
        "CRAFT", "FELTCRAFT", "KNITTING", "SEWING",
        "BUTTON", "BEAD", "BEADS", "PAINT YOUR OWN"
    ]):
        return ("Toys & Games", "Craft Kits & Creative Play")

    if any(k in n for k in ["PARTY", "BIRTHDAY", "CELEBRATION", "BUNTING", "BANNER", "CONFETTI", "PARTY BAGS"]):
        return ("Seasonal & Celebration", "Party Supplies")

    # -------- Garden & outdoor --------
    if any(k in n for k in [
        "GARDEN", "GROW YOUR OWN", "PLANTER", "PLANT POT",
        "FLOWER POT", "SEEDS", "BIRD FEEDER", "WINDMILL", "OUTDOOR"
    ]):
        return ("Garden & Outdoor", "Garden Decor & Accessories")

    # -------- Pets --------
    if any(k in n for k in ["DOG ", "CAT ", "DOG_", "CAT_", "PET ", "PET-"]):
        if "BOWL" in n:
            return ("Pets", "Pet Bowls & Feeding")
        return ("Pets", "Pet Accessories")

    # -------- Kids & baby --------
    if any(k in n for k in ["NURSERY", "BABY", "MOBILE", "RATTLE", "PRAM", "BUGGY"]):
        return ("Kids & Baby", "Nursery & Baby Accessories")

    # -------- Travel --------
    if any(k in n for k in ["TRAVEL CARD", "TRAVELCARD", "PASSPORT COVER", "LUGGAGE TAG"]):
        return ("Travel & Luggage", "Travel Accessories")

    # -------- Home & Office organisation --------
    if any(k in n for k in ["CALENDAR", "ORGANISER", "ORGANIZER", "FILE ", "FOLDER", "MAGAZINE RACK", "CLIPBOARD"]):
        return ("Home & Office", "Organisers & Filing")

    # -------- Cleaning & utility --------
    if any(k in n for k in ["FEATHER DUSTER", "DUSTER", "PEG BAG", "PEG BASKET"]):
        return ("Home & Living", "Cleaning & Utility")

    # -------- Fallback --------
    return ("Other", "Other")

cat_sub = products["product_name"].apply(classify_product_category)
products["category"] = cat_sub.apply(lambda x: x[0])
products["sub_category"] = cat_sub.apply(lambda x: x[1])

product_cols = [
    "product_id", "sku", "product_name", "category",
    "sub_category", "base_price", "is_active"
]
products = products[product_cols]

# ========= STORE TABLE =========
N_STORES = 1000
store_ids = random.sample(range(1, 1001), N_STORES)

store_types = [
    "SUPERCENTER",
    "NEIGHBORHOOD_MARKET",
    "ONLINE_FULFILLMENT",
    "DISTRIBUTION_CENTER",
    "SAM_CLUB",
    "EXPRESS"
]

stores = pd.DataFrame([
    {
        "store_id": store_ids[i],
        "store_name": f"Store {store_ids[i]}",
        "store_type": random.choice(store_types),
        "city": None,
        "state": None,
        "zip_code": None,
        "region": "GLOBAL"
    }
    for i in range(N_STORES)
])

# ========= TRANSACTION HEADER (NO TOTALS YET) =========
txn_header = (
    df[["InvoiceNo", "InvoiceDate", "CustomerID"]]
    .drop_duplicates()
    .rename(columns={
        "InvoiceNo": "transaction_id_raw",
        "InvoiceDate": "transaction_timestamp",
        "CustomerID": "customer_id"
    })
)

txn_header = txn_header.reset_index(drop=True)
txn_header["transaction_id"] = txn_header.index + 1

# Assign one home store per customer
store_id_list = stores["store_id"].tolist()
unique_customers = txn_header["customer_id"].dropna().unique()
customer_to_store = {
    cid: random.choice(store_id_list)
    for cid in unique_customers
}
txn_header["store_id"] = txn_header["customer_id"].map(customer_to_store)

# Map store_id -> store_type to derive channel
store_type_map = stores.set_index("store_id")["store_type"]
txn_header["store_type"] = txn_header["store_id"].map(store_type_map)

def infer_channel_from_store_type(store_type: str) -> str:
    if store_type is None or pd.isna(store_type):
        return "UNKNOWN"

    st = str(store_type).upper()

    if st == "ONLINE_FULFILLMENT":
        return "WEB"
    if st in ("SUPERCENTER", "NEIGHBORHOOD_MARKET", "EXPRESS", "SAM_CLUB"):
        return "STORE"
    if st in ("DISTRIBUTION_CENTER",):
        return "WHOLESALE"

    return "OTHER"

txn_header["channel"] = txn_header["store_type"].apply(infer_channel_from_store_type)

# Placeholders; will overwrite total_amount and set payment_method later
txn_header["total_amount"] = np.nan
# We'll create a payment_method_id and payment_method later
txn_header["payment_method_id"] = np.nan
txn_header["payment_method"] = None

# ========= TRANSACTION LINE ITEM =========
# Attach product_id via sku
df_line = df.merge(
    products[["product_id", "sku"]],
    left_on="StockCode",
    right_on="sku",
    how="left"
)

# Attach transaction_id via InvoiceNo + CustomerID
df_line = df_line.merge(
    txn_header[["transaction_id_raw", "transaction_id", "customer_id"]],
    left_on=["InvoiceNo", "CustomerID"],
    right_on=["transaction_id_raw", "customer_id"],
    how="left"
)

line_items = df_line[[
    "product_id", "transaction_id", "Quantity", "UnitPrice"
]].copy()

line_items["line_item_id"] = range(1, len(line_items) + 1)
line_items["quantity"] = line_items["Quantity"].astype(int)
line_items["unit_price"] = line_items["UnitPrice"].astype(float)
line_items["discount_amount"] = 0.0
line_items["promo_id"] = None

# line_amount for totals
line_items["line_amount"] = line_items["quantity"] * line_items["unit_price"]

tli_cols = [
    "line_item_id", "transaction_id", "product_id",
    "quantity", "unit_price", "discount_amount", "promo_id", "line_amount"
]
line_items = line_items[tli_cols]

# ========= AGGREGATE TOTALS INTO TRANSACTION HEADER =========
txn_agg = (
    line_items
    .groupby("transaction_id", as_index=False)
    .agg(total_amount=("line_amount", "sum"))
)

txn_header = txn_header.drop(columns=["total_amount"])
txn_header = txn_header.merge(txn_agg, on="transaction_id", how="left")

# ========= PAYMENT METHODS + ASSIGNMENT =========
payment_method = pd.DataFrame({
    "payment_method_id": [1, 2, 3, 4, 5],
    "method_name": [
        "CREDIT_CARD",
        "DEBIT_CARD",
        "CASH",
        "GIFT_CARD",
        "MOBILE_WALLET"
    ]
})

# Random assignment with distribution:
# 60% CREDIT_CARD, 20% DEBIT_CARD, 10% MOBILE_WALLET, 10% CASH
rand_vals = np.random.rand(len(txn_header))
pm_ids = []

for r in rand_vals:
    if r < 0.60:
        pm_ids.append(1)  # CREDIT_CARD
    elif r < 0.80:
        pm_ids.append(2)  # DEBIT_CARD
    elif r < 0.90:
        pm_ids.append(5)  # MOBILE_WALLET
    else:
        pm_ids.append(3)  # CASH

txn_header["payment_method_id"] = pm_ids

pm_map = payment_method.set_index("payment_method_id")["method_name"]
txn_header["payment_method"] = txn_header["payment_method_id"].map(pm_map)

# Drop helper column store_type before saving header
txn_header = txn_header.drop(columns=["store_type"])

txn_header_cols = [
    "transaction_id_raw",
    "transaction_id",
    "customer_id",
    "store_id",
    "transaction_timestamp",
    "channel",
    "total_amount",
    "payment_method_id",
    "payment_method"
]
txn_header = txn_header[txn_header_cols]

# ========= CUSTOMER LOYALTY PROFILE (from lifetime spend) =========
# Compute lifetime_spend per customer from transaction_header
cust_spend = (
    txn_header
    .groupby("customer_id", as_index=False)
    .agg(lifetime_spend=("total_amount", "sum"))
)

# Merge into full customer base (including those with no spend)
cust_spend_full = customers[["customer_id"]].merge(
    cust_spend, on="customer_id", how="left"
)
cust_spend_full["lifetime_spend"] = cust_spend_full["lifetime_spend"].fillna(0.0)

def tier_from_spend(x: float) -> str:
    if x < 500:
        return "BRONZE"
    elif x < 1000:
        return "SILVER"
    elif x < 2000:
        return "GOLD"
    else:
        return "PLATINUM"

cust_spend_full["loyalty_tier"] = cust_spend_full["lifetime_spend"].apply(tier_from_spend)
cust_spend_full["points_balance"] = np.floor(cust_spend_full["lifetime_spend"] / 10).astype(int)
cust_spend_full["enrollment_date"] = pd.to_datetime("2023-01-01")
cust_spend_full["last_activity_date"] = pd.to_datetime("2024-11-01")

customer_loyalty_profile = cust_spend_full[[
    "customer_id",
    "loyalty_tier",
    "points_balance",
    "enrollment_date",
    "last_activity_date",
    "lifetime_spend"
]]

# Update customers.loyalty_tier from loyalty_profile
customers = customers.drop(columns=["loyalty_tier"])
customers = customers.merge(
    customer_loyalty_profile[["customer_id", "loyalty_tier"]],
    on="customer_id",
    how="left"
)

# ========= PROMOTION TABLE =========
promo_rows = [
    {
        "promo_name": "New Customer 10% Off",
        "promo_type": "PERCENT_DISCOUNT",
        "discount_value": 10.00,
        "start_date": "2024-10-01",
        "end_date": "2024-12-31",
        "min_basket_amount": 0.00,
        "target_channel": "ALL",
        "is_active": 1
    },
    {
        "promo_name": "Web Order $15 Off 100+",
        "promo_type": "FIXED_DISCOUNT",
        "discount_value": 15.00,
        "start_date": "2024-11-01",
        "end_date": "2024-11-30",
        "min_basket_amount": 100.00,
        "target_channel": "WEB",
        "is_active": 1
    },
    {
        "promo_name": "App Flash 20% Weekend",
        "promo_type": "PERCENT_DISCOUNT",
        "discount_value": 20.00,
        "start_date": "2024-12-07",
        "end_date": "2024-12-08",
        "min_basket_amount": 30.00,
        "target_channel": "APP",
        "is_active": 1
    },
    {
        "promo_name": "Store Only $5 Off 40+",
        "promo_type": "FIXED_DISCOUNT",
        "discount_value": 5.00,
        "start_date": "2024-11-15",
        "end_date": "2024-12-31",
        "min_basket_amount": 40.00,
        "target_channel": "STORE",
        "is_active": 1
    },
    {
        "promo_name": "BOGO Snacks",
        "promo_type": "BOGO",
        "discount_value": 0.00,
        "start_date": "2024-11-01",
        "end_date": "2024-11-20",
        "min_basket_amount": 0.00,
        "target_channel": "ALL",
        "is_active": 1
    },
    {
        "promo_name": "Electronics Bundle Deal",
        "promo_type": "BUNDLE",
        "discount_value": 0.00,
        "start_date": "2024-12-01",
        "end_date": "2024-12-31",
        "min_basket_amount": 200.00,
        "target_channel": "ALL",
        "is_active": 1
    },
    {
        "promo_name": "We Miss You 25 Off 150+",
        "promo_type": "FIXED_DISCOUNT",
        "discount_value": 25.00,
        "start_date": "2024-12-01",
        "end_date": "2025-01-15",
        "min_basket_amount": 150.00,
        "target_channel": "ALL",
        "is_active": 1
    },
    {
        "promo_name": "Gold Tier 15%",
        "promo_type": "PERCENT_DISCOUNT",
        "discount_value": 15.00,
        "start_date": "2024-10-15",
        "end_date": "2024-12-31",
        "min_basket_amount": 0.00,
        "target_channel": "ALL",
        "is_active": 1
    }
]

promotion = pd.DataFrame(promo_rows)
promotion.insert(0, "promo_id", range(1, len(promotion) + 1))

# ========= PROMOTION ELIGIBILITY =========
promo_eligibility_list = []

cust_ids = customers["customer_id"].tolist()

# Helper: get promo row by name
def get_promo_row(name: str):
    row = promotion.loc[promotion["promo_name"] == name].iloc[0]
    return row["promo_id"], row["start_date"], row["end_date"]

# 1) New Customer 10% Off – all customers (CAMPAIGN)
promo_id_nc, start_nc, end_nc = get_promo_row("New Customer 10% Off")
for cid in cust_ids:
    promo_eligibility_list.append({
        "promo_id": promo_id_nc,
        "customer_id": cid,
        "eligibility_start_date": start_nc,
        "eligibility_end_date": end_nc,
        "eligibility_reason": "CAMPAIGN"
    })

# 2) Web Order $15 Off 100+ – ~20% customers (AB_TEST)
promo_id_web, start_web, end_web = get_promo_row("Web Order $15 Off 100+")
mask_20 = np.random.rand(len(cust_ids)) < 0.20
for cid, flag in zip(cust_ids, mask_20):
    if flag:
        promo_eligibility_list.append({
            "promo_id": promo_id_web,
            "customer_id": cid,
            "eligibility_start_date": start_web,
            "eligibility_end_date": end_web,
            "eligibility_reason": "AB_TEST"
        })

# 3) App Flash 20% Weekend – ~15% customers (APP_PUSH)
promo_id_app, start_app, end_app = get_promo_row("App Flash 20% Weekend")
mask_15 = np.random.rand(len(cust_ids)) < 0.15
for cid, flag in zip(cust_ids, mask_15):
    if flag:
        promo_eligibility_list.append({
            "promo_id": promo_id_app,
            "customer_id": cid,
            "eligibility_start_date": start_app,
            "eligibility_end_date": end_app,
            "eligibility_reason": "APP_PUSH"
        })

# 4) Gold Tier 15% – GOLD & PLATINUM only (LOYALTY_TIER)
promo_id_gold, start_gold, end_gold = get_promo_row("Gold Tier 15%")
gold_platinum_customers = customer_loyalty_profile.loc[
    customer_loyalty_profile["loyalty_tier"].isin(["GOLD", "PLATINUM"]),
    "customer_id"
].tolist()

for cid in gold_platinum_customers:
    promo_eligibility_list.append({
        "promo_id": promo_id_gold,
        "customer_id": cid,
        "eligibility_start_date": start_gold,
        "eligibility_end_date": end_gold,
        "eligibility_reason": "LOYALTY_TIER"
    })

promotion_eligibility = pd.DataFrame(promo_eligibility_list)

# ========= INVENTORY SNAPSHOT (store × product) =========
# Cross join store and product
inventory_snapshot = stores[["store_id"]].merge(
    products[["product_id"]],
    how="cross"
)

inventory_snapshot["snapshot_date"] = "2024-11-01"
inventory_snapshot["stock_level"] = np.random.randint(20, 220, size=len(inventory_snapshot))      # 20–219
inventory_snapshot["reorder_point"] = np.random.randint(20, 70, size=len(inventory_snapshot))     # 20–69
inventory_snapshot["on_order_qty"] = np.random.randint(0, 40, size=len(inventory_snapshot))       # 0–39

# ========= DROP HELPER COLUMNS & WRITE ALL CSVs =========
# Drop line_amount before writing line_items
line_items = line_items.drop(columns=["line_amount"])

customers.to_csv(OUTPUT_DIR / "customer.csv", index=False)
products.to_csv(OUTPUT_DIR / "product.csv", index=False)
stores.to_csv(OUTPUT_DIR / "store.csv", index=False)
txn_header.to_csv(OUTPUT_DIR / "transaction_header.csv", index=False)
line_items.to_csv(OUTPUT_DIR / "transaction_line_item.csv", index=False)
payment_method.to_csv(OUTPUT_DIR / "payment_method.csv", index=False)
promotion.to_csv(OUTPUT_DIR / "promotion.csv", index=False)
promotion_eligibility.to_csv(OUTPUT_DIR / "promotion_eligibility.csv", index=False)
inventory_snapshot.to_csv(OUTPUT_DIR / "inventory_snapshot.csv", index=False)
customer_loyalty_profile.to_csv(OUTPUT_DIR / "customer_loyalty_profile.csv", index=False)

print("Staging CSVs created in:", OUTPUT_DIR)
