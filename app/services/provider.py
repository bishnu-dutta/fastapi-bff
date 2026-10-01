from abc import ABC, abstractmethod
class BaseDataProvider(ABC):
    @abstractmethod
    async def create(self, collection: str, data: dict) -> dict: pass
    @abstractmethod
    async def get_by_id(self, collection: str, item_id: str | int) -> dict | None: pass
    @abstractmethod
    async def list(self, collection: str, filters: dict = None) -> list[dict]: pass
    @abstractmethod
    async def update(self, collection: str, item_id: str | int, data: dict) -> dict: pass
    @abstractmethod
    async def delete(self, collection: str, item_id: str | int) -> bool: pass

