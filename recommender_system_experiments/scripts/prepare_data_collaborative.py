import os
import json
import pickle
import logging
from typing import List, Dict, Any, Set
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from anyio import Path

# Configuration
PLAYLIST_COUNT_THRESHOLD = 20000
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_json(file_path: str) -> Dict[str, Any]:
    """Load a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
        return {}


def load_data_from_directory(directory: str) -> List[Dict[str, Any]]:
    """Load all JSON files from a directory using multithreading."""
    logger.info(f"Scanning directory: {directory}")
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]
    logger.info(f"Found {len(files)} JSON files")
    with ThreadPoolExecutor() as executor:
        return list(tqdm(executor.map(load_json, files), total=len(files), desc="Loading JSON files"))


def extract_playlists_and_tracks(data: List[Dict[str, Any]]) -> tuple[list[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Extract playlists and track metadata from raw input."""
    playlists = []
    tracks_dict = {}
    for data_item in tqdm(data, desc="Processing data"):
        if not data_item.get('playlists'):
            logger.warning("Skipping item with no playlists")
            continue
        for playlist in data_item['playlists']:
            playlists.append({
                'tracks': [track['track_uri'] for track in playlist['tracks']],
                'name': playlist['name']
            })
            for track in playlist['tracks']:
                tracks_dict[track['track_uri']] = track
    logger.info(f"Extracted {len(playlists)} playlists and {len(tracks_dict)} unique tracks")
    return playlists, tracks_dict


def count_tracks(playlists: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count occurrences of each track in all playlists."""
    counts = dict(Counter(track for playlist in playlists for track in playlist['tracks']))
    logger.info(f"Counted {len(counts)} unique track URIs")
    return counts


def filter_playlists_by_popular_presence(playlists: List[Dict[str, Any]], track_counts: Dict[str, int], threshold: int) -> tuple[List[Dict[str, Any]], Set[str]]:
    """
    Keep playlists that contain at least one track that appears in >= threshold playlists.
    Retain all tracks from those playlists.
    """
    popular_tracks = {track_uri for track_uri, count in track_counts.items() if count >= threshold}
    logger.info(f"Identified {len(popular_tracks)} popular tracks with threshold {threshold}")
    
    retained_playlists = []
    valid_tracks = set()
    
    for pl in tqdm(playlists, desc="Filtering playlists"):
        if any(track_uri in popular_tracks for track_uri in pl['tracks']):
            retained_playlists.append(pl)
            valid_tracks.update(pl['tracks'])  # include all tracks from retained playlists
    
    logger.info(f"{len(retained_playlists)} playlists retained after filtering by popular track presence")
    logger.info(f"{len(valid_tracks)} unique valid tracks found in retained playlists")
    return retained_playlists, valid_tracks


def save_pickle(obj: Any, path: Path) -> None:
    """Save an object as a pickle file."""
    try:
        with open(path, "wb") as f:
            pickle.dump(obj, f)
        logger.info(f"Saved pickle to {path}")
    except Exception as e:
        logger.error(f"Failed to save pickle to {path}: {e}")


def main() -> None:
    logger.info("Starting playlist processing pipeline")
    
    data = load_data_from_directory('../data')
    if not data:
        logger.error("No data loaded. Exiting.")
        return

    playlists, tracks_dict = extract_playlists_and_tracks(data)

    track_counts = count_tracks(playlists)
    filtered_playlists, valid_track_uris = filter_playlists_by_popular_presence(playlists, track_counts, PLAYLIST_COUNT_THRESHOLD)
    valid_tracks_dict = {track_uri: tracks_dict[track_uri] for track_uri in valid_track_uris}

    output_path = Path("data/02_processed")
    os.makedirs(output_path, exist_ok=True)

    save_pickle(filtered_playlists, output_path / "filtered_playlists_collaborative.pkl")
    save_pickle(valid_tracks_dict, output_path / "valid_tracks_collaborative.pkl")

    logger.info("Pipeline complete.")


if __name__ == "__main__":
    main()
