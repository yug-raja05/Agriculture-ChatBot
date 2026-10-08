from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, collection: AsyncIOMotorCollection, model: Type[ModelType]):
        self.collection = collection
        self.model = model

    async def get(self, id: str) -> Optional[ModelType]:
        doc = await self.collection.find_one({"_id": id})
        if doc:
            return self.model(**doc)
        return None

    async def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        doc = await self.collection.find_one({field_name: value})
        if doc:
            return self.model(**doc)
        return None

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        cursor = self.collection.find().skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            results.append(self.model(**doc))
        return results

    async def create(self, obj_in: ModelType) -> ModelType:
        # Export as dict, handling alias configuration
        data = obj_in.model_dump(by_alias=True)
        await self.collection.insert_one(data)
        return obj_in

    async def update(self, id: str, data: Dict[str, Any]) -> Optional[ModelType]:
        await self.collection.update_one({"_id": id}, {"$set": data})
        return await self.get(id)

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0
