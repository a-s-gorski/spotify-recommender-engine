import logging
import os
from typing import List

import joblib
from qdrant_client import AsyncQdrantClient
from sklearn.feature_extraction.text import TfidfVectorizer

from src.recommend.clustering.config import Settings

logger = logging.getLogger(__name__)


class ClusteringRecommendService:
    def __init__(self, settings: Settings):
        self.tokenizer_path = settings.tokenizer_path
        self.client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant__service__api__key)
        self.collection_name = settings.qdrant_collection_name
        self.vectorizer: TfidfVectorizer = joblib.load(self.tokenizer_path)

    async def recommend_tracks(
        self,
        playlist_name: str,
        k: int = 10,
        n_neighbors: int = 5
    ) -> List[str]:
        """
        Asynchronously recommend tracks from Qdrant based on a playlist name using TF-IDF vector similarity.

        Args:
            vectorizer: Fitted TfidfVectorizer for playlist names.
            playlist_name: Name of the query playlist.
            k: Max number of unique recommended tracks.
            n_neighbors: Number of similar playlists to retrieve.

        Returns:
            A list of up to `k` unique recommended track URIs.
        """
        logger.info(f"Querying Qdrant for playlist: '{playlist_name}'")

        query_vec = self.vectorizer.transform([playlist_name]).toarray()[0]

        search_result = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vec,
            limit=n_neighbors,
            with_payload=True
        )

        recommended_tracks = []
        for point in search_result:
            tracks = point.payload.get("tracks", [])
            recommended_tracks.extend(tracks)

        unique_tracks = list(dict.fromkeys(recommended_tracks))
        logging.info(f"Found {len(unique_tracks)} unique recommended tracks.")
        return unique_tracks[:k]
