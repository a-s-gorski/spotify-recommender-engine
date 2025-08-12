import pickle
import joblib
import logging
import os
from pathlib import Path
from tqdm import tqdm
from dotenv import find_dotenv, load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import create_engine, Column, Integer, String, ARRAY
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector
from concurrent.futures import ThreadPoolExecutor, as_completed
import dill
import numpy

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Constants
MIN_PLAYLIST_LENGTH = 5
INPUT_PATH = "data/02_processed"
VECTOR_DIM = 500
BATCH_SIZE = 500
NUM_WORKERS = 4  # Adjust to match your CPU or DB capabilities

# Load environment variables
env_file = find_dotenv()
if env_file:
    load_dotenv(env_file)

# DB settings
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "123456")
PG_DB = os.getenv("POSTGRES_DB", "testdb")

DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
print(f"Using database URL: {DATABASE_URL}")
# ORM setup
Base = declarative_base()

def store_pkl(obj, name, flavour = "joblib"):
	path = name
	if flavour == "joblib":
		joblib.dump(obj, path, compress = 9)
	elif flavour == "dill":
		with open(path, "wb") as dill_file:
			dill.dump(obj, dill_file)
	else:
		raise ValueError(flavour)


class Playlist(Base):
    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    tracks = Column(ARRAY(String), nullable=False)
    embedding = Column(Vector(VECTOR_DIM), nullable=False)


def setup_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

def filter_valid_tracks(playlists, valid_tracks):
    logging.info(f"Filtering playlists using {len(valid_tracks)} valid tracks...")
    filtered = []
    for pl in tqdm(playlists, total=len(playlists), desc="Filtering playlists"):
        filtered_tracks = [t for t in pl['tracks'] if t in valid_tracks]
        filtered.append({'name': pl['name'], 'tracks': filtered_tracks})
    logging.info(f"Filtered down to {len(filtered)} playlists.")
    return filtered

def upload_to_pgvector(main_session, name_vectors, names, tracks):
    logging.info("Uploading to pgvector in batches with multiple threads...")

    engine = main_session.get_bind()
    Session = sessionmaker(bind=engine)

    def insert_batch(batch_start):
        batch_end = min(batch_start + BATCH_SIZE, len(names))
        local_session = Session()
        try:
            batch = []
            for i in range(batch_start, batch_end):
                vector = name_vectors[i].toarray().flatten().tolist()
                playlist = Playlist(
                    name=names[i],
                    tracks=tracks[i],
                    embedding=vector
                )
                batch.append(playlist)
            local_session.add_all(batch)
            local_session.commit()
            logging.info(f"Inserted batch {batch_start}-{batch_end - 1}")
        except Exception as e:
            logging.error(f"Failed batch {batch_start}-{batch_end - 1}: {e}")
            local_session.rollback()
        finally:
            local_session.close()

    batch_starts = list(range(0, len(names), BATCH_SIZE))
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = [executor.submit(insert_batch, i) for i in batch_starts]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Uploading Batches"):
            f.result()  # will raise any exceptions

    logging.info("All batches uploaded.")

def main():
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
        max_features=VECTOR_DIM,
        stop_words='english',
        lowercase=True,
        token_pattern=r'\b\w+\b'
    )
    # vectorizer_pipeline = PMMLPipeline(
    # [
    #     ("vectorizer", vectorizer),
    # ]
    # )
    # vectorizer_pipeline.configure()
    name_vectors = vectorizer.fit_transform(names)
    logging.info("Vectorization complete.")
    
    
    store_pkl(vectorizer, "data/03_artifacts/vectorizer.pkl", flavour="joblib")
    logging.info("Saved vectorizer to 'vectorizer.pkl'.")

    session = setup_db()
    upload_to_pgvector(session, name_vectors, names, tracks)

if __name__ == "__main__":
    main()
