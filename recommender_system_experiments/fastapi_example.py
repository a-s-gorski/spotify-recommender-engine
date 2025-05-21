from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from collections import Counter
import uvicorn

app = FastAPI()

# Connect to MongoDB
# random password for demonstration purposes
mongo_uri = f"mongodb://admin:secret@localhost:27017"
client = MongoClient(mongo_uri)

db = client["spotify_recommender"]
playlists_col = db["playlists"]
track_playlists_col = db["track_playlists"]

class QueryPlaylist(BaseModel):
    track_uris: List[str]
    top_k: int = 100
    max_neighbors: int = 500

def find_similar_playlists(track_uris, max_neighbors=500):
    candidate_counts = Counter()
    for track in track_uris:
        doc = track_playlists_col.find_one({"_id": track}, {"playlists": 1})
        if doc and "playlists" in doc:
            candidate_counts.update(doc["playlists"])
    most_common = candidate_counts.most_common(max_neighbors)
    similar_pids = [pid for pid, _ in most_common]
    return similar_pids

def recommend_tracks(track_uris, top_k=100, max_neighbors=500):
    similar_pids = find_similar_playlists(track_uris, max_neighbors)
    track_counter = Counter()
    for pid in similar_pids:
        pl = playlists_col.find_one({"_id": pid}, {"tracks": 1})
        if pl:
            track_counter.update(pl["tracks"])
    existing_tracks = set(track_uris)
    recommendations = [t for t, _ in track_counter.most_common() if t not in existing_tracks]
    return recommendations[:top_k]

@app.post("/recommend/")
async def recommend(query: QueryPlaylist):
    if not query.track_uris:
        raise HTTPException(status_code=400, detail="track_uris must not be empty")
    recs = recommend_tracks(query.track_uris, top_k=query.top_k, max_neighbors=query.max_neighbors)
    return {"recommended_track_uris": recs}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
