# Python code to illustrate
from pymongo import MongoClient
  
try:
    conn = MongoClient('localhost', portnumber)
    print("Connected successfully!!!")
except:  
    print("Could not connect to MongoDB")
