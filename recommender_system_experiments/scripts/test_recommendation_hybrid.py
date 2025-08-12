import asyncio
import logging
import os
import time
from typing import List
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import find_dotenv, load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient

from test_recommendation_clustering_pgvector import recommend_clustering
from test_recommendation_collaborative import recommend_collaborative

env_file = find_dotenv()
if env_file:
    load_dotenv(env_file)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://username:password@host:port/database")  # Replace with your MongoDB URI
DB_NAME = "spotify"
TOP_K = 10

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def hybrid_recommendation(
    vectorizer: TfidfVectorizer,
    query_uris: List[str],
    playlist_name: str,
    client: AsyncIOMotorClient,
    k: int = TOP_K
) -> List[str]:
    collab_recs = await recommend_collaborative(client, query_uris, k)
    logging.info(f"Collaborative returned {len(collab_recs)} tracks")

    if len(collab_recs) >= k:
        return list(dict.fromkeys(collab_recs))[:k]

    remaining = k - len(collab_recs)
    cluster_recs = await recommend_clustering(vectorizer, playlist_name, k=remaining)
    logging.info(f"Qdrant fallback returned {len(cluster_recs)} tracks")

    combined = list(dict.fromkeys(collab_recs + cluster_recs))
    return combined[:k]

async def run_test_case(
    client: AsyncIOMotorClient,
    vectorizer: TfidfVectorizer,
    query_uris: List[str],
    playlist_name: str,
    expected_count: int = TOP_K,
    test_name: str = "Test"
) -> None:
    logging.info(f"Running {test_name} with {len(query_uris)} query tracks and playlist name '{playlist_name}'")
    start = time.perf_counter()
    recs = await hybrid_recommendation(vectorizer, query_uris, playlist_name, client, k=expected_count)
    elapsed = time.perf_counter() - start

    unique_recs = set(recs)
    logging.info(f"{test_name} returned {len(recs)} tracks ({len(unique_recs)} unique) in {elapsed:.3f} sec")
    if len(recs) < expected_count:
        logging.warning(f"{test_name} returned fewer tracks ({len(recs)}) than expected ({expected_count})")
    if len(recs) != len(unique_recs):
        logging.warning(f"{test_name} returned duplicate tracks")

    logging.info(f"\n{test_name} recommendations:")
    for i, track_uri in enumerate(recs, 1):
        logging.info(f"{i}. {track_uri}")

async def main():
    client = AsyncIOMotorClient(MONGO_URI)
    vectorizer: TfidfVectorizer = joblib.load("data/03_artifacts/vectorizer.pkl")

    test_cases = [
        {
            "query_uris": [
                "spotify:track:7ouMYWpwJ422jRcDASZB7P",
                "spotify:track:1f6zKZ0I1ChZ0zsZt4AZqW"
            ],
            "playlist_name": "chill lofi beats",
            "expected_count": TOP_K,
            "test_name": "Normal test with valid tracks"
        },
        {
            "query_uris": [
                "spotify:track:4uLU6hMCjMI75M1A2tKUQC",
                "spotify:track:1301WleyT98MSxVHPZCA6M",
                "spotify:track:6habFhsOp2NvshLv26DqMb"
            ],
            "playlist_name": "upbeat workout mix",
            "expected_count": TOP_K,
            "test_name": "Another normal test with different valid tracks"
        },
        {
            "query_uris": [],
            "playlist_name": "empty query test",
            "expected_count": TOP_K,
            "test_name": "Test with empty query tracks list"
        },
        {
            "query_uris": [
                "spotify:track:nonexistent1",
                "spotify:track:nonexistent2",
                "spotify:track:nonexistent3"
            ],
            "playlist_name": "random non-existent tracks",
            "expected_count": TOP_K,
            "test_name": "Test with query tracks not present in DB"
        },
    ]

    for test in test_cases:
        await run_test_case(client, vectorizer=vectorizer, **test)

    client.close()

if __name__ == "__main__":
    asyncio.run(main())