from typing import List

from motor.motor_asyncio import AsyncIOMotorClient

from src.recommend.collaborative.config import Settings
from src.recommend.collaborative.recommend import recommend_collaborative


class CollaborativeRecommendService:
    def __init__(self, settings: Settings):
        self.db_name = settings.mongo_db_name
        self.mongo_uri = settings.mongo_uri
        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db_name = settings.mongo_db_name
        self.max_neighbors = settings.mongo_max_neightbors

    async def recommend_tracks(
        self,
        query_uris: List[str],
        k: int = 10,
    ) -> List[str]:
        """
        Recommend tracks based on collaborative filtering from MongoDB.

        Args:
            query_uris: List of seed track URIs.
            k: Max number of recommended tracks.
            max_neighbors: Max number of playlists to consider.

        Returns:
            List of recommended track URIs.
        """
        return await recommend_collaborative(self.client, query_uris, k, self.max_neighbors, self.db_name)
