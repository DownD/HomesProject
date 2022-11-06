"""
Module the interfaces with the MongoDB
"""

import logging
from typing import List

import pymongo

LOGGER = logging.getLogger("DBHandler")
DB_NAME = "houses"


class DBHandler:
    """_summary_"""

    def __init__(
        self, host: str, port: int, db_name: str = DB_NAME
    ):

        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = pymongo.MongoClient(host, port)
        self.db_client = self.client[db_name]
        LOGGER.debug("Connected to database %s", db_name)

    def insert_house(self, data: dict, collection_name: str):
        """
        Insert a house in the database.
        If the house already exists, it will be updated


        Args:
            data (dict): json data specifying the house
            collection_name (str): name of the collection to insert the house
        """
        collection = self.db_client[collection_name]

        # Check if already exists in db
        old_record = collection.find_one({"_id": data["_id"]})
        if old_record:

            # If the new record is different from the old one, update it
            if data != old_record:
                collection.update_one(
                    {"_id": data["_id"]}, {"$set": data}
                )
                LOGGER.debug(
                    "House %s was updated into the DB %s",
                    data["_id"],
                    collection_name,
                )

            else:
                # If the new record is the same as the old one, don't do anything
                LOGGER.debug(
                    "House already exists in db, no action was preformed"
                )
                return

        else:
            # If the house doesn't exist yet, insert it
            collection.insert_one(data)
            LOGGER.debug(
                "New house %s has been added to the collection %s",
                data["_id"],
                collection_name,
            )

    def insert_houses(self, data: List[dict], collection_name: str):
        """
        Insert a house in the database

        Args:
            data (List[dict]): a list of houses in json format to be inserted in to the DB
            collection_name (str): name of the collection to insert the house
        """

        raise NotImplementedError()

    def get_latest_house(self, collection_name: str):
        """
        Get the latest house inserted in the database

        Args:
            collection_name (str): name of the collection to insert the house

        Returns:
            dict: the latest house inserted in the database
        """

        LOGGER.debug("Getting latest house from collection %s", collection_name)
        collection = self.db_client[collection_name]
        return collection.find_one(sort=[("data_scrapped", -1)])

    def close(self):
        """
        Close the connection to the database
        """
        self.client.close()
