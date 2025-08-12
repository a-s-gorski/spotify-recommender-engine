import logging
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer

from src.recommend.clustering.models import Playlist
from sqlalchemy import select
from src.recommend.clustering.engine import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def recommend_clustering(
    vectorizer: TfidfVectorizer,
    playlist_name: str,
    k: int = 10,
    n_neighbors: int = 5
) -> List[str]:
    logging.info(f"Querying pgvector for playlist: '{playlist_name}'")
    query_vec = vectorizer.transform([playlist_name]).toarray()[0].tolist()

    async with AsyncSessionLocal() as session:
        stmt = (
            select(Playlist)
            .order_by(Playlist.embedding.l2_distance(query_vec))
            .limit(n_neighbors)
        )
        result = await session.execute(stmt)
        similar_playlists = result.scalars().all()

    logger.info(f"Retrieved {len(similar_playlists)} similar playlists.")

    recommended_tracks = []
    for pl in similar_playlists:
        recommended_tracks.extend(pl.tracks)

    unique_tracks = list(dict.fromkeys(recommended_tracks))
    logger.info(f"Found {len(unique_tracks)} unique recommended tracks.")
    return unique_tracks[:k]

