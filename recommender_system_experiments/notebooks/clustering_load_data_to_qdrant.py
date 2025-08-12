import asyncio
import numpy as np
from tqdm.asyncio import tqdm_asyncio
from qdrant_client import QdrantClient, models as rest
from dotenv import load_dotenv
import os

load_dotenv()



# ---- CONFIG ----
QDRANT_URL = "https://ede2a3a4-b5e3-418b-8b33-c78597d0190d.europe-west3-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "playlists"
VECTOR_DIM = 768           # Adjust if your real vectors differ
NUM_PLAYLISTS = 1000       # For testing, reduce to avoid crashes
BATCH_SIZE = 300           # Batch size for uploads
MAX_CONCURRENCY = 4        # Simultaneous batches

# ---- Qdrant Client ----
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

# ---- Dummy Playlist Data ----
def generate_dummy_data(n, dim):
    playlists = [{"name": f"Playlist {i}", "tracks": [f"track_{i}_1", f"track_{i}_2"]} for i in range(n)]
    name_vectors = np.random.rand(n, dim).astype("float32")
    return playlists, name_vectors

# ---- Sparse to Dense (if needed) ----
def sparse_vec_to_dense_list(vec):
    return vec.tolist()

# ---- Main Upload Function ----
async def load_playlists_to_qdrant(client: QdrantClient, collection_name, playlists, name_vectors):
    # Delete and recreate collection
    existing_collections = [c.name for c in await asyncio.to_thread(client.get_collections)]
    if collection_name in existing_collections:
        print(f"Deleting existing collection '{collection_name}'...")
        await asyncio.to_thread(client.delete_collection, collection_name)

    print(f"Creating collection '{collection_name}' with vector dim={name_vectors.shape[1]}")
    await asyncio.to_thread(client.recreate_collection,
        collection_name=collection_name,
        vectors_config=rest.VectorParams(
            size=name_vectors.shape[1],
            distance=rest.Distance.COSINE
        )
    )

    sem = asyncio.Semaphore(MAX_CONCURRENCY)

    async def upsert_batch(start_idx):
        async with sem:
            batch = []
            for i in range(start_idx, min(start_idx + BATCH_SIZE, len(playlists))):
                vec = name_vectors[i]
                batch.append(rest.PointStruct(
                    id=i,
                    vector=sparse_vec_to_dense_list(vec),
                    payload={
                        "playlist_name": playlists[i]['name'],
                        "tracks": playlists[i]['tracks']
                    }
                ))
            await asyncio.to_thread(client.upsert, collection_name=collection_name, points=batch)

    tasks = [
        upsert_batch(i)
        for i in range(0, len(playlists), BATCH_SIZE)
    ]

    print(f"Uploading {len(playlists)} playlists in {len(tasks)} batches...")
    await tqdm_asyncio.gather(*tasks, desc="Upserting to Qdrant")

    print(f"✅ Done: {len(playlists)} playlists loaded into '{collection_name}'.")

# ---- Entry Point ----
if __name__ == "__main__":
    playlists, name_vectors = generate_dummy_data(NUM_PLAYLISTS, VECTOR_DIM)
    asyncio.run(load_playlists_to_qdrant(qdrant_client, COLLECTION_NAME, playlists, name_vectors))
