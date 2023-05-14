from pymongo import MongoClient


class MongoCRUD:
    def __init__(self, database_name):
        self.database_name = database_name
        self.client = MongoClient()
        self.db = self.client[self.database_name]

    def update_one(self, collection_name, query, target, data):

        # Define the update operation to add a value to the list

        update = {"$push": {target: data}}
        self.db.update_one(query, update)

    def insert_data(self, collection_name, data):
        # Connect to the database

        collection = self.db[collection_name]

        if not type(data) == type([]):
            result = collection.insert_one(data)
            return result

        else:
            # Insert data into the collection
            result = collection.insert_many(data)

            # Print the result
            # print(
            #     f"Inserted {len(result.inserted_ids)} documents into '{self.database_name}.{collection_name}' collection.")

            # Close the connection
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
        collection = self.db[collection_name]

        # Retrieve documents based on filter query and projection fields
        documents = []
        for doc in collection.find(filter_query, projection_fields):
            documents.append(doc)

        return documents
