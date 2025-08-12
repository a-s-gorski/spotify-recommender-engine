import asyncio
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Any

from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from tqdm.asyncio import tqdm_asyncio  # async tqdm for async loops
from tqdm import tqdm  # for sync loops
from dotenv import find_dotenv, load_dotenv
import os
import random

env_file = find_dotenv()
if env_file:
    load_dotenv(env_file)

INPUT_PATH = Path("data/02_processed")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://username:password@host:port/database")
print(f"Using MongoDB URI: {MONGO_URI}")
DB_NAME = "spotify"
BATCH_SIZE = 1000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

from pydantic import Field


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


def filter_valid_tracks(
    playlists: List[Dict[str, Any]],
    valid_tracks: Dict[str, Any]
) -> List[Dict[str, Any]]:
    filtered = []
    for pl in tqdm(playlists, desc="Filtering playlists"):
        filtered_tracks = [t for t in pl['tracks'] if t in valid_tracks]
        filtered.append({'name': pl['name'], 'tracks': filtered_tracks})
    return filtered


def batched(iterable: List[Any], n: int):
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]


async def load_data_to_mongo(
    client: AsyncIOMotorClient,
    valid_tracks_dict: Dict[str, Dict[str, Any]],
    filtered_playlists: List[Dict[str, Any]],
    batch_size: int = BATCH_SIZE,
) -> None:
    db = client[DB_NAME]

    logging.info("Dropping existing collections...")
    await db.tracks.drop()
    await db.playlists.drop()

    logging.info(f"Inserting {len(valid_tracks_dict)} tracks...")
    track_docs = [Track(**{"_id": uri, **meta}) for uri, meta in valid_tracks_dict.items()]
    if track_docs:
        for batch in tqdm(list(batched(track_docs, batch_size)), desc="Inserting tracks batches"):
            await Track.insert_many(batch)

    playlist_docs = [Playlist(name=pl['name'], tracks=pl['tracks']) for pl in filtered_playlists]
    playlist_docs = random.sample(playlist_docs, k = int(0.2 * len(playlist_docs)))

    total_batches = (len(playlist_docs) + batch_size - 1) // batch_size
    logging.info(f"Inserting {len(playlist_docs)} playlists in {total_batches} batches...")

    for batch in tqdm(batched(playlist_docs, batch_size), total=total_batches, desc="Inserting playlist batches"):
        await Playlist.insert_many(batch)

    logging.info("✅ Data loaded into MongoDB.")


async def main():
    logging.info("Loading input data...")

    with open(INPUT_PATH / "filtered_playlists_collaborative.pkl", "rb") as f:
        playlists = pickle.load(f)

    with open(INPUT_PATH / "valid_tracks_collaborative.pkl", "rb") as f:
        valid_tracks_dict = pickle.load(f)

    logging.info("Filtering playlists...")
    filtered_playlists = filter_valid_tracks(playlists, valid_tracks_dict)

    logging.info("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URI,
                                serverSelectionTimeoutMS=1200000,  # 120s to select server
                                connectTimeoutMS=1200000,          # 60s to establish connection
                                socketTimeoutMS=1200000,           # 60s for read/write socket operations
                                maxPoolSize=100,                 # (Optional) Increase pool size
                                waitQueueTimeoutMS=600000         # (Optional) How long to wait for a connection from pool
                                )

    logging.info("Initializing Beanie ODM...")
    await init_beanie(database=client[DB_NAME], document_models=[Playlist, Track])

    await load_data_to_mongo(client, valid_tracks_dict, filtered_playlists)
    
    client.close()



if __name__ == "__main__":
    asyncio.run(main())
