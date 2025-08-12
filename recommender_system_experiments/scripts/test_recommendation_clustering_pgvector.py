import logging
import time
import joblib
import asyncio
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import Integer, String, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, sessionmaker
from pgvector.sqlalchemy import Vector
from sqlalchemy import select

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Async database config
PG_HOST = "localhost"
PG_PORT = "5432"
PG_USER = "postgres"
PG_PASSWORD = "123456"
PG_DB = "testdb"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

VECTOR_DIM = 500

# Async SQLAlchemy base
class Base(DeclarativeBase):
    pass

class Playlist(Base):
    __tablename__ = "playlists"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False)
    tracks = mapped_column(ARRAY(String), nullable=False)
    embedding = mapped_column(Vector(VECTOR_DIM), nullable=False)

# Async engine + session
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

# Async recommendation function
async def recommend_clustering(
    vectorizer: TfidfVectorizer,
    playlist_name: str,
    k: int = 10,
    n_neighbors: int = 5
) -> List[str]:
    logging.info(f"Querying pgvector for playlist: '{playlist_name}'")
    query_vec = vectorizer.transform([playlist_name]).toarray()[0].tolist()

    async with AsyncSessionLocal() as session:
        stmt = (
            select(Playlist)
            .order_by(Playlist.embedding.l2_distance(query_vec))
            .limit(n_neighbors)
        )
        result = await session.execute(stmt)
        similar_playlists = result.scalars().all()

    logging.info(f"Retrieved {len(similar_playlists)} similar playlists.")

    recommended_tracks = []
    for pl in similar_playlists:
        recommended_tracks.extend(pl.tracks)

    unique_tracks = list(dict.fromkeys(recommended_tracks))
    logging.info(f"Found {len(unique_tracks)} unique recommended tracks.")
    return unique_tracks[:k]

# Async test wrapper
async def test_recommendation_async():
    vectorizer: TfidfVectorizer = joblib.load("data/03_artifacts/vectorizer.pkl")
    test_name = "chill lofi beats"

    start_time = time.perf_counter()
    recommendations = await recommend_clustering(vectorizer, test_name, k=10, n_neighbors=5)
    elapsed = time.perf_counter() - start_time

    logging.info(f"Recommendations for '{test_name}': (took {elapsed:.3f} seconds)")
    for i, track in enumerate(recommendations, 1):
        print(f"{i}. {track}")

if __name__ == "__main__":
    logging.info("Starting async recommendation test...")
    asyncio.run(test_recommendation_async())
