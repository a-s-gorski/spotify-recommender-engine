import logging
import asyncio
import time
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from collections import Counter
import os
from dotenv import find_dotenv, load_dotenv
from beanie import Document, init_beanie
from pydantic import Field

env_file = find_dotenv()
if env_file:
    load_dotenv(env_file)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:secret@localhost:27017")
DB_NAME = "spotify"
MAX_NEIGHBORS = 50
TOP_K = 10

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class Playlist(Document):
    name: str
    tracks: List[str]

    class Settings:
        name = "playlists"

class Track(Document):
    id: str = Field(alias="_id")  # Track URI as _id
    pos: int
    artist_name: str
    track_uri: str
    artist_uri: str
    track_name: str
    album_uri: str
    duration_ms: int
    album_name: str

    class Settings:
        name = "tracks"

# === Collaborative filtering recommendation ===

async def recommend_collaborative(
    client: AsyncIOMotorClient,
    query_uris: List[str],
    k: int = TOP_K,
    max_neighbors: int = MAX_NEIGHBORS
) -> List[str]:
    """
    Recommend tracks from MongoDB based on shared playlist co-occurrence using async Motor.

    Args:
        client: Async MongoDB client.
        query_uris: List of seed track URIs.
        k: Max number of recommended tracks.
        max_neighbors: Max number of playlists to consider.

    Returns:
        List of recommended track URIs.
    """
    db = client[DB_NAME]

    logging.info(f"Querying MongoDB for {len(query_uris)} seed tracks...")

    query_start = time.perf_counter()
    cursor = db.playlists.find(
        {"tracks": {"$in": query_uris}},
        {"tracks": 1}
    ).limit(max_neighbors)

    track_counter = Counter()
    matched_playlists = 0
    async for doc in cursor:
        track_counter.update(doc["tracks"])
        matched_playlists += 1
    query_elapsed = time.perf_counter() - query_start

    logging.info(f"Matched {matched_playlists} playlists in {query_elapsed:.3f} sec.")
    logging.info(f"Collected {len(track_counter)} unique tracks.")

    # Remove query tracks from recommendations
    recommended = [t for t, _ in track_counter.most_common() if t not in query_uris]
    return recommended[:k]

async def test_recommendation() -> None:
    """
    Connects to MongoDB, initializes Beanie ODM, and tests the recommender with a fixed query track list.
    Logs time taken and prints the recommendations.
    """
    client = AsyncIOMotorClient(MONGO_URI)

    logging.info("Initializing Beanie ODM...")
    await init_beanie(database=client[DB_NAME], document_models=[Playlist, Track])

    query_uris = [
        "spotify:track:7ouMYWpwJ422jRcDASZB7P", 
        "spotify:track:1f6zKZ0I1ChZ0zsZt4AZqW",
        "spotify:track:2xYxC1vTNrzGP1IzpOtevG",
        "spotify:track:6bBccEe8gvwl6KJZf293Je",
        "spotify:track:7e7lYBH4xPqBiYqlY04u9o",
        "spotify:track:5bAw3HrcuaQvJ5fNuFD4wx", 
    ]

    total_start = time.perf_counter()
    recommendations = await recommend_collaborative(client, query_uris)
    total_elapsed = time.perf_counter() - total_start

    logging.info(f"Top {len(recommendations)} recommendations (total time: {total_elapsed:.3f} sec):")
    for i, track in enumerate(recommendations, 1):
        print(f"{i}. {track}")

    client.close()

if __name__ == "__main__":
    asyncio.run(test_recommendation())
