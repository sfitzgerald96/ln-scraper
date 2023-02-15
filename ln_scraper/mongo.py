# Python code to illustrate
from pymongo import MongoClient


class DB:
    def __init__(self, host, port, db_name='loopnet'):
        self.host = host
        self.port = port
        self._client = MongoClient(host, port)
        self._db = self._client[db_name]

    def add_one_listing(self, results):
        self._db["listing"].insert_one(results)
