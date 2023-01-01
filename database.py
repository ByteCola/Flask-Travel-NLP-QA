from bson import ObjectId
from pymongo import MongoClient


class Database(object):

    def __init__(self, ip="localhost", port=27017):
        self.ip = ip
        self.port = port
        self.conn = MongoClient(self.ip, self.port)

    def connect_database(self, database_name):
        return self.conn[database_name]

    def get_collection(self, database_name, collection_name):
        return self.connect_database(database_name).get_collection(collection_name)

if __name__ == '__main__':

   database = Database()
   user_col = database.get_collection('sight_qa_db', 'user_data')
   user_data = user_col.find_one({"_id": ObjectId('6288984d98913e002c04d497')})
   print(user_data)