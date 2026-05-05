import pymongo

## MONGO_HOST = '10.65.164.153'   ## using EC2 Private IPv4 addresses for AWS@Emory
MONGO_HOST = '44.202.116.81'   ## using EC2 Public IPv4 addresses for AWS@Academy Learner Lab
MONGO_PORT = 27017
MONGO_DB_NAME = "test_database"
MONGO_COLLECTION_NAME = "test_collection"

conn_str = 'mongodb://<mongo-host>:<mongodb-ip>/'
conn_str = conn_str.replace('<mongo-host>', MONGO_HOST).replace('<mongodb-ip>', str(MONGO_PORT))
print('conn_str=' + conn_str)
client = pymongo.MongoClient(conn_str)

## Your implementation goes below !!!
db = client[MONGO_DB_NAME]

##Specify the collection to be used
collection = db[MONGO_COLLECTION_NAME]

##Insert a single document
single_doc = {"name": "Amy", "address": "Apple st 652"}
print("insert one document")
collection.insert_one(single_doc)

##Insert multiple documents
multi_docs = [
    {"name": "Hannah", "address": "Mountain 21"},
    {"name": "Michael", "address": "Valley 345"},
    {"name": "Sandy", "address": "Ocean blvd 2"},
    {"name": "Betty", "address": "Green Grass 1"},
    {"name": "Richard", "address": "Sky st 331"},
    {"name": "Susan", "address": "One way 98"},
    {"name": "Vicky", "address": "Yellow Garden 2"},
    {"name": "Ben", "address": "Park Lane 38"},
    {"name": "William", "address": "Central st 954"},
    {"name": "Chuck", "address": "Main Road 989"},
    {"name": "Viola", "address": "Sideway 1633"}
]

print("insert multiple documents")
collection.insert_many(multi_docs)

## List documents use limit
myresult = collection.find().limit(100)

# print the result:
for x in myresult:
    print(x)

##Close the connection
client.close()