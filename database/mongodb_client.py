from pymongo import MongoClient


class MongoCRUD:
    def __init__(self, database_name):
        self.database_name = database_name

    def insert_data(self, collection_name, data):
        # Connect to the database
        client = MongoClient()
        db = client[self.database_name]
        collection = db[collection_name]

        if not type(data) == type([]):
            data = [data]
        # Insert data into the collection
        result = collection.insert_many(data)

        # Print the result
        # print(
        #     f"Inserted {len(result.inserted_ids)} documents into '{self.database_name}.{collection_name}' collection.")

        # Close the connection
        client.close()

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
        client = MongoClient()
        database = client[self.database_name]
        collection = database[collection_name]

        # Retrieve documents based on filter query and projection fields
        documents = []
        for doc in collection.find(filter_query, projection_fields):
            documents.append(doc)

        # Close database connection
        client.close()

        return documents
