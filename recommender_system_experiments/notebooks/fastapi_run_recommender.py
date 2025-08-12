from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import asyncio
import pickle

from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, SearchRequest
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# Load vectorizer and track dict
with open("vectorizer.pkl", "rb") as f:
    vectorizer: TfidfVectorizer = joblib.load(f)

with open("processed/01_filtered/valid_tracks.pkl", "rb") as f:
    valid_tracks_dict = pickle.load(f)

QDRANT_URL = "https://ede2a3a4-b5e3-418b-8b33-c78597d0190d.europe-west3-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "playlists"

app = FastAPI()

class RecommendRequest(BaseModel):
    playlist_name: str
    k: int = 10
    n_neighbors: int = 5

@app.post("/recommend", response_model=List[str])
async def recommend(request: RecommendRequest):
    try:
        query_vec = vectorizer.transform([request.playlist_name]).toarray()[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Vectorizer failed: {str(e)}")

    client = AsyncQdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=30)

    try:
        search_result = await client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vec.tolist(),
            limit=request.n_neighbors,
            timeout=30
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Qdrant query timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Qdrant query failed: {str(e)}")

    recommended_tracks = []
    for point in search_result.points:
        tracks = point.payload.get("tracks", [])
        recommended_tracks.extend(tracks)

    return list(dict.fromkeys(recommended_tracks))[:request.k]

@app.get("/track-names", response_model=List[str])
def get_track_names(track_uris: List[str]):
    return [valid_tracks_dict.get(uri, {}).get('track_name', 'unknown') for uri in track_uris]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
