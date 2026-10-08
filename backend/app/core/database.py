import logging
import asyncio
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from app.core.config import settings

logger = logging.getLogger(__name__)

class InMemoryCollection:
    def __init__(self, parent_db=None):
        self._data: Dict[str, dict] = {}
        self.parent_db = parent_db

    async def find_one(self, filter_dict: dict) -> Optional[dict]:
        for doc in self._data.values():
            match = True
            for k, v in filter_dict.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return doc.copy()
        return None

    async def insert_one(self, doc: dict) -> dict:
        doc_id = str(doc.get("_id") or doc.get("id") or len(self._data) + 1)
        self._data[doc_id] = doc.copy()
        if self.parent_db and hasattr(self.parent_db, 'save'):
            self.parent_db.save()
        return doc

    async def update_one(self, filter_dict: dict, update_dict: dict) -> Optional[dict]:
        doc = await self.find_one(filter_dict)
        if doc:
            doc_id = str(doc.get("_id") or doc.get("id"))
            if "$set" in update_dict:
                for k, v in update_dict["$set"].items():
                    doc[k] = v
            if "$addToSet" in update_dict:
                for k, v in update_dict["$addToSet"].items():
                    arr = doc.get(k, [])
                    if isinstance(arr, list) and v not in arr:
                        arr.append(v)
                    doc[k] = arr
            self._data[doc_id] = doc
            if self.parent_db and hasattr(self.parent_db, 'save'):
                self.parent_db.save()
        return doc

    async def count_documents(self, filter_dict: dict) -> int:
        count = 0
        for doc in self._data.values():
            match = True
            for k, v in filter_dict.items():
                if k == "sender" and isinstance(v, dict) and "$in" in v:
                    if doc.get(k) not in v["$in"]:
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                count += 1
        return count

    def find(self, filter_dict: dict):
        class InMemoryCursor:
            def __init__(self, data_list):
                self.data_list = data_list
                self._iter = None

            def sort(self, key, direction=1):
                reverse = direction == -1
                try:
                    self.data_list.sort(key=lambda x: x.get(key, ""), reverse=reverse)
                except Exception:
                    pass
                return self

            def limit(self, n):
                self.data_list = self.data_list[:n]
                return self

            def __aiter__(self):
                self._iter = iter(self.data_list)
                return self

            async def __anext__(self):
                try:
                    return next(self._iter)
                except StopIteration:
                    raise StopAsyncIteration

        matches = []
        for doc in self._data.values():
            match = True
            for k, v in filter_dict.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                matches.append(doc.copy())
        return InMemoryCursor(matches)

    async def delete_one(self, filter_dict: dict):
        doc = await self.find_one(filter_dict)
        if doc:
            doc_id = str(doc.get("_id") or doc.get("id"))
            self._data.pop(doc_id, None)

    async def delete_many(self, filter_dict: dict):
        to_delete = []
        for doc_id, doc in list(self._data.items()):
            match = True
            for k, v in filter_dict.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                to_delete.append(doc_id)
        for doc_id in to_delete:
            self._data.pop(doc_id, None)

    async def replace_one(self, filter_dict: dict, doc: dict, upsert: bool = False):
        existing = await self.find_one(filter_dict)
        if existing:
            doc_id = str(existing.get("_id") or existing.get("id"))
            self._data[doc_id] = doc.copy()
        elif upsert:
            doc_id = str(doc.get("_id") or doc.get("id"))
            self._data[doc_id] = doc.copy()

import json
import os

class InMemoryDatabase:
    """
    High-performance in-memory database fallback when remote MongoDB Atlas connection times out or is unreachable.
    Includes simple JSON file persistence to prevent data loss across server reloads.
    """
    def __init__(self):
        self._collections: Dict[str, InMemoryCollection] = {}
        self.persist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "local_db.json")
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.persist_path):
                with open(self.persist_path, "r") as f:
                    data = json.load(f)
                    for coll_name, coll_data in data.items():
                        coll = InMemoryCollection(parent_db=self)
                        coll._data = coll_data
                        self._collections[coll_name] = coll
        except Exception as e:
            logger.error(f"Failed to load local DB: {e}")

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
            with open(self.persist_path, "w") as f:
                data = {name: coll._data for name, coll in self._collections.items()}
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to save local DB: {e}")

    def __getitem__(self, name: str) -> InMemoryCollection:
        if name not in self._collections:
            self._collections[name] = InMemoryCollection(parent_db=self)
        return self._collections[name]

class DatabaseManager:
    def __init__(self):
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self._in_memory_db = InMemoryDatabase()

    def connect(self):
        """
        Connect to MongoDB database with 3-second timeout and fallback.
        """
        try:
            logger.info("Configuring MongoDB Atlas connection client...")
            self.mongo_client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=3000,
                connectTimeoutMS=3000,
                socketTimeoutMS=5000
            )
            self.db = self.mongo_client[settings.MONGODB_DB_NAME]
            logger.info("MongoDB client initialized with 3s connection timeout.")
        except Exception as e:
            logger.warning(f"Remote MongoDB client setup failed ({e}). Using active in-memory database driver.")
            self.db = self._in_memory_db

    def close(self):
        """
        Close database connections.
        """
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed.")

db_manager = DatabaseManager()

def get_db():
    """
    Dependency helper returning active database instance.
    """
    if db_manager.db is None:
        db_manager.connect()
    return db_manager.db
