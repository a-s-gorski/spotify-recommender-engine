import logging
import asyncio
import time
from typing import List
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from qdrant_client.async_qdrant_client import AsyncQdrantClient

RECOMMEND_QDRANT_URL = "localhost"
RECOMMEND_QDRANT_PORT = 6333
RECOMMEND_COLLECTION = "playlists"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def recommend_clustering(
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
    logging.info(f"Querying Qdrant for playlist: '{playlist_name}'")
    query_vec = vectorizer.transform([playlist_name]).toarray()[0]

    client = AsyncQdrantClient(
        url=RECOMMEND_QDRANT_URL,
        port=RECOMMEND_QDRANT_PORT
    )

    search_result = await client.search(
        collection_name=RECOMMEND_COLLECTION,
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

async def test_recommendation() -> None:
    """
    Loads the vectorizer and tests the recommendation function with a sample playlist name,
    logging how long the recommendation took.
    """
    vectorizer: TfidfVectorizer = joblib.load("data/03_artifacts/vectorizer.pkl")
    test_name = "chill lofi beats"

    start_time = time.perf_counter()
    recommendations = await recommend_clustering(vectorizer, test_name, k=10, n_neighbors=5)
    elapsed = time.perf_counter() - start_time

    logging.info(f"Recommendations for '{test_name}': (took {elapsed:.3f} seconds)")
    for i, track in enumerate(recommendations, 1):
        print(f"{i}. {track}")
    

if __name__ == "__main__":
    asyncio.run(test_recommendation())
