import logging
from typing import List

import joblib
from qdrant_client import AsyncQdrantClient
from sklearn.feature_extraction.text import TfidfVectorizer

from src.recommend.clustering.config import Settings
from src.recommend.clustering.recommend import recommend_clustering

logger = logging.getLogger(__name__)


class ClusteringRecommendService:
    def __init__(self, settings: Settings):
        self.tokenizer_path = settings.tokenizer_path
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
        return await recommend_clustering(
            vectorizer=self.vectorizer,
            playlist_name=playlist_name,
            k=k,
            n_neighbors=n_neighbors
        )
