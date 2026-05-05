Managing Big Data Final Group Project - Code Documentation
Team 10

------------------------------------------------------------------------------------------------------------------
Part 1
OLTP Data Loading & Initialization Guide (MySQL)
 
0. Prerequisites
Before beginning the OLTP loading process, ensure the following:
 
- Local MySQL Server installed (recommended: MySQL Workbench).
- Python 3.10+ environment with required packages:
    • pandas
    • mysql-connector-python
- Access to the following project files:
    • UCI Online Retail II Dataset (CSV)
    • Loading_Data.py
    • Creating_Tables.sql
    • Inserts.sql
- A database schema name prepared (e.g., walmart_oltp).
 
1. Download the Online Retail II Dataset
Download the dataset from the UCI Machine Learning Repository:
https://archive.ics.uci.edu/ml/datasets/Online+Retail+II
 
Save the CSV file into a local directory, for example:
    /Data/online_retail_II.csv
 
2. Configure and Run Loading_Tables.py
This script prepares the raw dataset, performs cleaning, generates synthetic IDs, and exports the final OLTP-ready master data tables.
 
2.1 Update the File Path
Modify the following line inside Loading_Tables.py:
    df = pd.read_csv("PATH_TO_DATASET/online_retail_II.csv")
Update it to point to your actual dataset location.
 
2.2 Script Responsibilities
The script performs:
- Cleaning raw UCI data (removing nulls, fixing invalid rows, deduplication)
- Standardizing column names and formats
- Generating synthetic identifiers:
      customer_id, product_id, store_id
- Constructing OLTP master datasets:
      customer, product, store, inventory, payment_method
- Exporting cleaned CSVs for SQL ingestion.
 
2.3 Output Files
Exports will appear in:
    C:/data/walmart_oltp/loading/customer.csv
    C:/data/walmart_oltp/loading/product.csv
    C:/data/walmart_oltp/loading/store.csv
    C:/data/walmart_oltp/loading/inventory_snapshot.csv
    C:/data/walmart_oltp/loading/payment_method.csv
    C:/data/walmart_oltp/loading/customer_loyalty_profile.csv
    C:/data/walmart_oltp/loading/transaction_line_item.csv
    C:/data/walmart_oltp/loading/transaction_header.csv
    C:/data/walmart_oltp/loading/promotion_eligibility.csv
    C:/data/walmart_oltp/loading/promotion.csv
 
2.4 Execute the Script:
    python Loading_Tables.py
 
3. Create a MySQL Connection in MySQL Workbench
1. Open MySQL Workbench.
2. Click the '+' icon next to MySQL Connections.
3. Configure the connection:
      Connection Name: Walmart OLTP
      Hostname: localhost (or RDS endpoint)
      Port: 3306
      Username: <your-username>
4. Test Connection → enter password.
5. Click OK to save the connection.
 
4. Run Walmart_DDL_Create_Tables.sql
This script initializes the relational schema and creates all OLTP tables.
 
Steps:
1. Open MySQL Workbench.
2. Open the Walmart OLTP connection.
3. File → Open SQL Script → select Creating_Tables.sql
4. Click Execute.
 
This will:
- Create the schema (e.g., walmart_oltp)
- Define tables: customer, product, store, inventory, payment_method
- Apply all necessary primary/foreign keys and constraints.
 
5. Run Walmart_DML_Inserts.sql to Populate OLTP Tables
After tables are created, bulk load all cleaned CSV data.
 
Steps:
1. Open Inserts.sql in MySQL Workbench.
2. Execute the script.
 
The script handles loading via LOAD DATA LOCAL INFILE, so no additional verification statements are required.
 
Summary Workflow Overview
1. Download UCI Online Retail II dataset
2. Update dataset path and run Loading_Data.py
3. Create MySQL Workbench connection
4. Execute Creating_Tables.sql
5. Execute Inserts.sql

------------------------------------------------------------------------------------------------------------------
Walmart NoSQL Data Pipeline & Analysis

This project implements a data pipeline to build a Customer 360 Operational Store for Walmart using AWS S3 for raw storage and MongoDB for the NoSQL operational database. It includes scripts for Extract-Transform-Load (ETL), data verification, and business analytics querying.
File Overview
1. Walmart_MongoDB.py (The ETL Script)
Purpose:
This is the main driver script. It connects to an AWS S3 bucket, reads raw CSV files, performs data transformations using Pandas, and loads the data into MongoDB.
* Raw Ingestion: Loads transaction_header, transaction_line_item, promotion, promotion_eligibility, and customer_loyalty_profile into their own collections.
* Feature Engineering: Aggregates transaction history and merges it with loyalty data to create a high-value CustomerFeatures collection (Customer 360 view).
2. Walmart_MongoDB_VerifyData.py (Verification)
Purpose:
A utility script to confirm that the ETL process was successful.
* Connects to the MongoDB database (walmart_nosql).
* Counts the number of documents in every collection.
* Prints the totals to the console for quick validation.
3. Walmart_MongoDB_SampleQueries.py (Analysis)
Purpose:
A query tool demonstrating how to extract business value from the NoSQL store.
* Customer 360: Look up specific customer profiles.
* Loyalty Analytics: Analyze spending habits by tier (Gold, Platinum, etc.).
* Promotions: Check active promotions and specific customer eligibility.
* Points Analysis: Aggregate average loyalty points per tier.
 Prerequisites
1. Python 3.x installed.
2. MongoDB Instance (EC2 or Atlas) running and accessible.
3. AWS S3 Bucket containing the source CSV files in a data/ folder.
4. Python Libraries:
pip install pandas boto3 pymongo

Configuration
Before running the scripts, you must update the Configuration Section at the top of Walmart_MongoDB.py and the other files.
1. AWS Credentials (Required for Lab Environments)
Update the following variables in Walmart_MongoDB.py:
AWS_ACCESS_KEY_ID = "YOUR_ASIA_..."
AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_KEY"
AWS_SESSION_TOKEN = "YOUR_LONG_SESSION_TOKEN" # Critical for Student/Lab accounts
S3_BUCKET_NAME = "project-bucket-0444"      # Ensure this matches your actual bucket

2. MongoDB Connection
Update the MONGO_URI in ALL THREE files (Walmart_MongoDB.py, Walmart_MongoDB_VerifyData.py, Walmart_MongoDB_SampleQueries.py).
# Replace with your current EC2 Public IP
MONGO_URI = "mongodb://44.200.178.89:27017/"

Note: If you restart your AWS Lab, this IP address will change, and you must update it in all files.
Usage Instructions
Run the scripts in the following order:
Step 1: Run the ETL Pipeline
Extracts data from S3, transforms it, and populates MongoDB.
python Walmart_MongoDB.py
Expected Output:
--- Ingesting data/promotion.csv into promotion ---
Reading data/promotion.csv from bucket project-bucket-0444...
Successfully inserted 8 documents into 'promotion'.

--- Ingesting data/promotion_eligibility.csv into promotion_eligibility ---
Reading data/promotion_eligibility.csv from bucket project-bucket-0444...
Successfully inserted 10787 documents into 'promotion_eligibility'.

--- Ingesting data/customer_loyalty_profile.csv into customer_loyalty_profile ---
Reading data/customer_loyalty_profile.csv from bucket project-bucket-0444...
Successfully inserted 5955 documents into 'customer_loyalty_profile'.

--- Building Customer Features ---
Reading data/transaction_header.csv from bucket project-bucket-0444...
Reading data/transaction_line_item.csv from bucket project-bucket-0444...
Reading data/customer_loyalty_profile.csv from bucket project-bucket-0444...
Merging transaction data with loyalty profile...
Inserted 5955 documents into 'CustomerFeatures'.

Step 2: Verify the Data
Confirm that all collections are populated correctly.
python Walmart_MongoDB_VerifyData.py

Expected Output:
--- Verifying Database: walmart_nosql ---

Collection 'CustomerFeatures': 5,955 documents
Collection 'transaction_header': 44,941 documents
Collection 'transaction_line_item': 827,246 documents
Collection 'promotion': 8 documents
Collection 'promotion_eligibility': 10,787 documents
Collection 'customer_loyalty_profile': 5,955 documents

Total Documents: 894,892

Step 3: Run Analysis Queries
Execute the sample business queries to generate insights.
python Walmart_MongoDB_SampleQueries.py

Expected Output:
--- Average Loyalty Points by Tier ---
Tier            | Count      | Avg Points     
---------------------------------------------
PLATINUM        | 1622       | 861.31
GOLD            | 1083       | 140.68
SILVER          | 1109       | 72.30
BRONZE          | 2141       | 19.31

--- First 3 GOLD Customers ---
ID: 16698 | Spend: $1998.00 | Points: 199
ID: 14628 | Spend: $1998.00 | Points: 199
ID: 13630 | Spend: $1995.68 | Points: 199

--- Searching for Customer ID: 12347 ---
{ 'LastPurchaseDate': '2011-12-07 15:52:00',
  'NumOrders': 8,
  'TotalSpend': 5633.32,
  '_id': ObjectId('69327fc23cc82736364c260c'),
  'customer_id': 12347,
  'enrollment_date': '2023-01-01',
  'last_activity_date': '2024-11-01',
  'lifetime_spend': 5633.32,
  'loyalty_tier': 'PLATINUM',
  'points_balance': 563}

--- Checking Eligibility for Customer: 12347 ---
Eligible for: New Customer 10% Off (Reason: CAMPAIGN)
Eligible for: Gold Tier 15% (Reason: LOYALTY_TIER)

Troubleshooting
Error: ServerSelectionTimeoutError
   * Cause: The script cannot reach MongoDB.
   * Fix:
   1. Check if your EC2 instance is running.
   2. Verify the Public IP in MONGO_URI matches the EC2 instance.
   3. Ensure your AWS Security Group allows inbound traffic on Port 27017 from your IP.
Error: InvalidAccessKeyId or AccessDenied
   * Cause: AWS credentials are incorrect or expired.
   * Fix:
   1. Copy fresh credentials from your AWS Lab Dashboard.
   2. Ensure you included the AWS_SESSION_TOKEN.
   3. Verify S3_BUCKET_NAME is correct and accessible by your user.

------------------------------------------------------------------------------------------------------------------
Hive Data Warehouse Implementation Guide

0. Prerequisites
Before starting, ensure:
- AWS account with S3 and EMR access
- CSV data files:
 • transaction_header.csv
 • transaction_line_item.csv
 • promotion.csv
 • promotion_eligibility.csv
 • customer_loyalty_profile.csv
 • inventory_snapshot.csv
- EMR cluster with Hive and HDFS (minimum 3 cores for smooth functioning)
- SSH key pair (.pem file)

1. Upload Data to S3
Upload the CSV files into the S3 bucket:
<your-s3-bucket>

Paths:
s3://<your-s3-bucket>/transaction_header.csv
s3://<your-s3-bucket>/transaction_line_item.csv
s3://<your-s3-bucket>/promotion.csv
s3://<your-s3-bucket>/promotion_eligibility.csv
s3://<your-s3-bucket>/customer_loyalty_profile.csv
s3://<your-s3-bucket>/inventory_snapshot.csv

2. SSH into EMR Master Node
ssh -i "/path/to/key.pem" hadoop@<EMR-MASTER-PUBLIC-DNS>

3. Create HDFS Directories and Copy Data from S3
hdfs dfs -mkdir -p /user/hadoop/walmart


hdfs dfs -cp s3://<your-s3-bucket>/transaction_header.csv /user/hadoop/walmart/ 
hdfs dfs -cp s3://<your-s3-bucket>/transaction_line_item.csv /user/hadoop/walmart/
hdfs dfs -cp s3://<your-s3-bucket>/promotion.csv /user/hadoop/walmart/
hdfs dfs -cp s3://<your-s3-bucket>/promotion_eligibility.csv /user/hadoop/walmart/
hdfs dfs -cp s3://<your-s3-bucket>/customer_loyalty_profile.csv /user/hadoop/walmart/
hdfs dfs -cp s3://<your-s3-bucket>/inventory_snapshot.csv /user/hadoop/walmart/

4. Start Hive and Create Database
hive
CREATE DATABASE IF NOT EXISTS walmart_dw;
USE walmart_dw;

5. Create Raw External Tables (Schema-on-Read)
Transaction Header:
CREATE EXTERNAL TABLE IF NOT EXISTS txn_header_raw (transaction_id BIGINT, customer_id BIGINT, store_id INT, transaction_ts TIMESTAMP, payment_method_code STRING, total_amount DECIMAL(10,2), total_discount DECIMAL(10,2), promo_id STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '/user/hadoop/walmart' TBLPROPERTIES ("skip.header.line.count"="1");

Transaction Line Item:
CREATE EXTERNAL TABLE IF NOT EXISTS txn_items_raw (line_item_id BIGINT, transaction_id BIGINT, product_id BIGINT, quantity INT, unit_price DECIMAL(10,2), discount_amount DECIMAL(10,2), promo_id STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '/user/hadoop/walmart' TBLPROPERTIES ("skip.header.line.count"="1");

Promotion:
CREATE EXTERNAL TABLE IF NOT EXISTS promotion_raw (promo_id STRING, promo_description STRING, start_date DATE, end_date DATE, discount_type STRING, discount_value DECIMAL(10,2)) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '/user/hadoop/walmart' TBLPROPERTIES ("skip.header.line.count"="1");

Promotion Eligibility:
CREATE EXTERNAL TABLE IF NOT EXISTS promotion_eligibility_raw (promo_id STRING, customer_id BIGINT, eligibility_ts TIMESTAMP) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '/user/hadoop/walmart' TBLPROPERTIES ("skip.header.line.count"="1");

Customer Loyalty:
CREATE EXTERNAL TABLE IF NOT EXISTS loyalty_raw (customer_id BIGINT, loyalty_tier STRING, points_balance INT, last_activity_ts TIMESTAMP, lifetime_value DECIMAL(10,2)) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '/user/hadoop/walmart' TBLPROPERTIES ("skip.header.line.count"="1");
Inventory Snapshot:
CREATE EXTERNAL TABLE IF NOT EXISTS inventory_snapshot_raw (inventory_snapshot_id BIGINT, store_id BIGINT, product_id BIGINT, snapshot_date DATE, stock_level INT, reorder_point INT, on_order_qty INT) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '/user/hadoop/walmart' TBLPROPERTIES ("skip.header.line.count"="1");

6. Create the Unified Fact Table

DROP TABLE IF EXISTS fact_retail_txn_item;

CREATE TABLE fact_retail_txn_item (transaction_id BIGINT, line_item_id BIGINT, customer_id BIGINT, store_id INT, product_id BIGINT, transaction_ts TIMESTAMP, transaction_date DATE, quantity INT, gross_amount DECIMAL(10,2), discount_amount DECIMAL(10,2), net_amount DECIMAL(10,2), promo_id STRING, loyalty_tier STRING, points_balance INT, txn_date_str STRING, inventory_snapshot_date DATE, stock_level INT, reorder_point INT, on_order_qty INT) STORED AS TEXTFILE;

7. Populate Fact Table
INSERT OVERWRITE TABLE fact_retail_txn_item SELECT i.transaction_id, i.line_item_id, h.customer_id, h.store_id, i.product_id, h.transaction_ts, TO_DATE(h.transaction_ts), i.quantity, i.quantity * i.unit_price, i.discount_amount, (i.quantity * i.unit_price) - i.discount_amount, COALESCE(i.promo_id, h.promo_id), l.loyalty_tier, l.points_balance, CAST(TO_DATE(h.transaction_ts) AS STRING), inv.snapshot_date, inv.stock_level, inv.reorder_point, inv.on_order_qty FROM txn_items_raw i JOIN txn_header_raw h ON i.transaction_id = h.transaction_id LEFT JOIN loyalty_raw l ON h.customer_id = l.customer_id LEFT JOIN inventory_snapshot inv ON inv.store_id = h.store_id AND inv.product_id = i.product_id AND inv.snapshot_date = TO_DATE(h.transaction_ts);

8. Verify Fact Table
SELECT COUNT(*) FROM fact_retail_txn_item;
SELECT * FROM fact_retail_txn_item LIMIT 10;

------------------------------------------------------------------------------------------------------------------
Part 2: Walmart GreenCart App

The GreenCart Advisor is a full-stack sustainability recommendation system integrated into Walmart’s backend architecture. It extends the OLTP schema with sustainability attributes, generates synthetic sustainability data, loads it into MySQL, and exposes a real-time web front-end via Streamlit.

1. Purpose
Part 2 introduces a new business application that Walmart does not currently offer: a real-time advisor that recommends eco-friendly product substitutes based on sustainability metrics, customer preferences, and price sensitivity.
This part contains:
   * New sustainability datasets
   * New OLTP tables
   * Python data generators
   * Streamlit UI for live recommendations
   * Logging of recommendation/acceptance decisions into MySQL

2. File List

File			Description
greencart_ddl.sql	Creates GreenCart-specific OLTP tables (sustainability, preferences, recommendations, feedback)
seed_csv.py		Generates synthetic sustainability and customer preference CSVs
load_data.sql		Loads CSVs into MySQL using LOAD DATA LOCAL INFILE
greencart_app.py	Full Streamlit application for running the recommender UI

3. Prerequisites
Software Requirements
   * Python 3.10+
   * MySQL 8.0+
   * Streamlit
   * Pandas
   * Pymysql
   * NumPy

Install dependencies:
pip install streamlit pandas pymysql numpy

MySQL Configuration:
   * Enable local file loading for CSV import:
   * SET GLOBAL local_infile=1;
   * Ensure the MySQL user has FILE, INSERT, SELECT Permissions.

4. Step-by-Step Execution Guide

STEP 1 — Create GreenCart Tables
Run in MySQL Workbench or CLI:
SOURCE greencart_ddl.sql;

STEP 2 — Create CSV to load Data
Run the Python generator:
python seed_csv.py
python Loading_Tables.py

STEP 3 — Load Data into MySQL
Run:
SOURCE load_data.sql;

STEP 4 — Launch the GreenCart Streamlit App
Run:
streamlit run greencart_app.py

5. How the Recommendation Engine Works

Component		Description
sustainability_gain	alt.overall_score – orig.overall_score
price_diff		alt.price – orig.price
brand_match		1 if same brand else 0
weights			user-tuned sliders
	

The scoring formula in greencart_app.py:
score = (
    normalized_sustainability_gain * env_weight
    - normalized_price_diff        * price_weight
    + brand_match                  * brand_weight
)

6. Outputs Generated
   * Sustainability-enhanced OLTP tables
   * Logged recommendation events
   * Customer adoption data

------------------------------------------------------------------------------------------------------------------------------------------------------------
Part 3: Walmart GreenCart Data Warehouse and Insights

Part 3 builds a fully functional star schema for sustainability-driven analytics and loads OLTP data into a dimensional model to support decision-making queries and visualizations.

1. Purpose
   * Convert OLTP recommendation logs into a dimensional warehouse
   * Enable business insights such as segmentation, price elasticity, sustainability ROI, and product risk analysis
   * Provide visualizations for reporting

2. File List

File				Description
walmart_dw.sql			Creates star schema (dimensions + fact table)
etl_walmart_dw.sql		Full ETL pipeline from OLTP → DW
seed_dim_date.py		Generates a complete date dimension
seed_recommendations.py		Generates synthetic recommendation logs in OLTP
green_insights_and_plots.py	Runs analytical queries + produces visualizations
	
3. Star Schema Overview

The DW schema includes:
Dimension Tables
   * dim_date
   * dim_customer
   * dim_loyalty_tier
   * dim_sustainability_goal
   * dim_channel
   * dim_store
   * dim_product

Fact Table
   * fact_green_recommendation
Contains one row per recommendation event:
   * customer_key
   * product_orig_key
   * product_alt_key
   * store_key
   * channel_key
   * date_key
   * sust_gain_points
   * price_diff
   * accepted_flag

4. Step-by-Step Execution Guide (Part 3)

STEP 1 — Create the Warehouse Schema
Run:
SOURCE walmart_dw.sql;

STEP 2 — Generate DimDate Table
Run:
python seed_dim_date.py

STEP 3 — Seed Recommendation Events in OLTP
Run:
python seed_recommendations.py

STEP 4 — Run the ETL Pipeline into DW
Run:
SOURCE etl_walmart_dw.sql;

STEP 5 — Generate Insights & Visualizations
Run:
python green_insights_and_plots.py

This script produces (All charts will appear in the working directory.): 
Q1 – Acceptance by Loyalty Tier
Identify which customer segments adopt sustainable products most.
Q2 – Price vs Sustainability Gain
Trade-off visualization by category.
Q3 – Channel Effectiveness
STORE vs WEB acceptance.
Q4 – Monthly Adoption Trend
Time-series showing GreenCart adoption.
Q5 – Sustainability Goal Segmentation
High-goal customers adopt 4–8% more.
Q6 – Category Green ROI
Which categories generate the best trade-off.
Q7 – Price Elasticity Curve
How price premiums affect acceptance.
Q8 – Sustainability Gain Response Curve
Does higher sustainability always increase acceptance?
Q9 – Store-Level Adoption
Top city/state combinations.
Q10 – Lifetime Customer GreenScore
Identifies Walmart’s “green champions.”
Q11 – Sustainability & Carbon by Loyalty Tier
Shows which segments buy low-carbon products.
Q12 – Category Carbon Impact
Helps Walmart decide where to focus carbon reduction.

5. Data Flow Summary (End-to-End)
[ OLTP Product + Customer + sustainability Tables ]
            |
            V
[ Loading_Tables.py ] → Walmart Data CSVs
[ seed_csv.py ] → Sustainability Data CSVs
            |
            v
[ load_data.sql ] → MySQL
            |
            v
[ greencart_app.py ] → Recommendation Logs
            |
            v
[ seed_recommendations.py ] → Synthetic Event Generation
            |
            v
============= ETL BEGINS =============
            |
            v
[ walmart_dw.sql ] → Dimensions + Fact
[ etl_walmart_dw.sql ] → Transfer to DW
            |
            v
[ green_insights_and_plots.py ] → Analytics

6. Troubleshooting

MySQL LOAD DATA error
Enable:
SET GLOBAL local_infile=1;

Streamlit MySQL connection issues
Check credentials inside greencart_app.py under:
db = pymysql.connect(
    host="localhost",
    user="root",
    password="...",
    db="walmart_dwh"
)
