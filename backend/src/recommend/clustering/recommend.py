import logging
from typing import List

from qdrant_client.async_qdrant_client import AsyncQdrantClient
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


async def recommend_clustering(
    client: AsyncQdrantClient,
    collection_name: str,
    vectorizer: TfidfVectorizer,
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
    query_vec = vectorizer.transform([playlist_name]).toarray()[0]

    search_result = await client.search(
        collection_name=collection_name,
        query_vector=query_vec,
        limit=n_neighbors,
        with_payload=True
    )

    recommended_tracks = []
    for point in search_result:
        tracks = point.payload.get("tracks", [])
        recommended_tracks.extend(tracks)

    await client.close()

    unique_tracks = list(dict.fromkeys(recommended_tracks))
    logging.info(f"Found {len(unique_tracks)} unique recommended tracks.")
    return unique_tracks[:k]
