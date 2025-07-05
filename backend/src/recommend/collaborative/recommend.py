import logging
from collections import Counter
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


async def recommend_collaborative(
    client: AsyncIOMotorClient,
    query_uris: List[str],
    k: int = 10,
    max_neighbors: int = 500,
    db_name: str = "spotify"
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
    db = client[db_name]

    logging.info(f"Querying MongoDB for {len(query_uris)} seed tracks...")

    cursor = db.playlists.find(
        {"tracks": {"$in": query_uris}},
        {"tracks": 1}
    ).limit(max_neighbors)

    track_counter = Counter()
    matched_playlists = 0
    async for doc in cursor:
        track_counter.update(doc["tracks"])
        matched_playlists += 1

    logger.info(f"Matched {matched_playlists} playlists.")
    logger.info(f"Collected {len(track_counter)} unique tracks.")

    recommended = [t for t, _ in track_counter.most_common()
                   if t not in query_uris]
    return recommended[:k]
