from pymongo import MongoClient


class MongoCRUD:
    def __init__(self, database_name):
        self.database_name = database_name

    def update_one(self, collection_name, query, target, data):
        client = MongoClient('mongodb://localhost:27017/')
        db = client[self.database_name]
        collection = db[collection_name]

        # Define the update operation to add a value to the list
        update = {"$push": {target: data}}
        collection.update_one(query, update)

    def insert_one(self, collection_name, data):
        client = MongoClient('mongodb://localhost:27017/')
        db = client[self.database_name]
        collection = db[collection_name]
        result = collection.insert_one(data)
        return result

    def insert_many(self, collection_name, data):
        client = MongoClient('mongodb://localhost:27017/')
        db = client[self.database_name]
        collection = db[collection_name]
        result = collection.insert_many(data)
        return result

    def get_data(self, collection_name, filter_query={}, projection_fields=None):
        """
        Retrieve documents from a MongoDB collection based on a filter query and projection fields.

        Parameters:
        -----------
        database_name (str): Name of the MongoDB database to connect to.
        collection_name (str): Name of the collection to retrieve documents from.
        filter_query (dict): A dictionary containing filter query parameters.
        projection_fields (dict or None): A dictionary containing projection field names.

        Returns:
        --------
        A list of matching documents from the specified collection.
        """
        # Connect to MongoDB server
        client = MongoClient('mongodb://localhost:27017/')
        db = client[self.database_name]
        collection = db[collection_name]

        # # Retrieve documents based on filter query and projection fields
        # for doc in collection.find(filter_query, projection_fields):
        #     yield doc
        return list(collection.find(filter_query, projection_fields))

    def get_one(self, collection_name, filter_query={}, projection_fields=None):
        """
        Retrieve documents from a MongoDB collection based on a filter query and projection fields.

        Parameters:
        -----------
        database_name (str): Name of the MongoDB database to connect to.
        collection_name (str): Name of the collection to retrieve documents from.
        filter_query (dict): A dictionary containing filter query parameters.
        projection_fields (dict or None): A dictionary containing projection field names.

        Returns:
        --------
        A list of matching documents from the specified collection.
        """
        # Connect to MongoDB server
        client = MongoClient('mongodb://localhost:27017/')
        db = client[self.database_name]
        collection = db[collection_name]

        # Retrieve documents based on filter query and projection fields
        return collection.find_one(filter_query, projection_fields)
