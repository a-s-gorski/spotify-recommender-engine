import pickle
import joblib
import asyncio
import logging
import os
from pathlib import Path
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct as AsyncPointStruct
from qdrant_client.models import VectorParams, Distance
from dotenv import find_dotenv, load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MIN_PLAYLIST_LENGTH = 5
QDRANT_URL = "http://localhost:6333"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "playlists"
QDRANT_BATCH_SIZE = 512
INPUT_PATH = "data/02_processed"
QDRANT_SECRET_API_KEY = os.environ.get("QDRANT__SERVICE__API_KEY", None)

def filter_valid_tracks(playlists, valid_tracks):
    logging.info(f"Filtering playlists using {len(valid_tracks)} valid tracks...")
    filtered = []
    for pl in tqdm(playlists, total=len(playlists), desc="Filtering playlists"):
        filtered_tracks = [t for t in pl['tracks'] if t in valid_tracks]
        filtered.append({'name': pl['name'], 'tracks': filtered_tracks})
    logging.info(f"Filtered down to {len(filtered)} playlists.")
    return filtered

async def upload_to_qdrant(name_vectors, names, tracks, vector_dim):
    logging.info("Connecting to Qdrant...: ")
    print(f"Using Qdrant at {QDRANT_URL}:{QDRANT_PORT} with API key: {QDRANT_SECRET_API_KEY}")
    client = AsyncQdrantClient(url=QDRANT_URL, api_key=QDRANT_SECRET_API_KEY)

    collections = await client.get_collections()
    if QDRANT_COLLECTION in [c.name for c in collections.collections]:
        logging.info(f"Deleting existing collection '{QDRANT_COLLECTION}'...")
        await client.delete_collection(QDRANT_COLLECTION)

    logging.info(f"Creating collection '{QDRANT_COLLECTION}' with vector size {vector_dim}...")
    await client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE)
    )

    sem = asyncio.Semaphore(8)
    total = len(names)
    logging.info(f"Uploading {total} playlists to Qdrant in batches of {QDRANT_BATCH_SIZE}...")

    async def upload_batch(start_idx):
        async with sem:
            end_idx = min(start_idx + QDRANT_BATCH_SIZE, total)
            logging.debug(f"Uploading batch {start_idx} to {end_idx - 1}")
            batch_names = names[start_idx:end_idx]
            batch_vectors = name_vectors[start_idx:end_idx]
            batch_tracks = tracks[start_idx:end_idx]

            points = [
                AsyncPointStruct(
                    id=start_idx + i,
                    vector=vec.toarray().flatten().tolist(),
                    payload={"name": name, "tracks": tr}
                )
                for i, (name, vec, tr) in enumerate(zip(batch_names, batch_vectors, batch_tracks))
            ]

            await client.upsert(collection_name=QDRANT_COLLECTION, points=points)
            logging.info(f"Uploaded batch {start_idx}–{end_idx - 1} ({len(points)} points)")

    tasks = [upload_batch(i) for i in range(0, total, QDRANT_BATCH_SIZE)]
    for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Uploading to Qdrant"):
        await f

    logging.info("Upload completed. Closing Qdrant connection.")
    await client.close()

def main():
    env_file = find_dotenv()
    if env_file:
        load_dotenv(env_file)
        logging.info(f"Loaded environment variables from {env_file}")
    
    logging.info("Loading playlist data...")
    with open(Path(INPUT_PATH) / "filtered_playlists_clustering.pkl", "rb") as f:
        playlists = pickle.load(f)

    with open(Path(INPUT_PATH) / "valid_tracks_clustering.pkl", "rb") as f:
        valid_tracks_dict = pickle.load(f)

    logging.info(f"Loaded {len(playlists)} playlists.")

    filtered = filter_valid_tracks(playlists, valid_tracks_dict)
    filtered = [p for p in filtered if len(p['tracks']) >= MIN_PLAYLIST_LENGTH]
    logging.info(f"Retained {len(filtered)} playlists with at least {MIN_PLAYLIST_LENGTH} tracks.")

    names = [p['name'] for p in filtered]
    tracks = [p['tracks'] for p in filtered]

    logging.info("Fitting TF-IDF vectorizer on playlist names...")
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        lowercase=True,
        token_pattern=r'\b\w+\b'
    )
    name_vectors = vectorizer.fit_transform(names)
    logging.info("Vectorization complete.")

    joblib.dump(vectorizer, "data/03_artifacts/vectorizer.pkl")
    logging.info("Saved vectorizer to 'vectorizer.pkl'.")

    asyncio.run(upload_to_qdrant(name_vectors, names, tracks, vector_dim=name_vectors.shape[1]))

if __name__ == "__main__":
    main()
