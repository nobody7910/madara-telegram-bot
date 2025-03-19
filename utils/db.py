import pymongo
from config import MONGO_URI
import logging

logger = logging.getLogger(__name__)

class Pixel:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(MONGO_URI)
            self.db = self.client['madara_bot']
            logger.info("Connected to MongoDB successfully!")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def close(self):
        self.client.close()
        logger.info("MongoDB connection closed.")

# Singleton instance
db_instance = None

def get_db():
    global db_instance
    if db_instance is None:
        db_instance = Pixel()
    return db_instance