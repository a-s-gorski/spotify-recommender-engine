import logging
from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials

from src.auth.controller import AuthController
from src.auth.router import bearer_scheme
from src.recommend.clustering.config import settings as clustering_settings
from src.recommend.clustering.service import ClusteringRecommendService
from src.recommend.collaborative.config import \
    settings as collaborative_settings
from src.recommend.collaborative.service import CollaborativeRecommendService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommend", tags=["recommend"])

clustering_service = ClusteringRecommendService(clustering_settings)
collaborative_service = CollaborativeRecommendService(collaborative_settings)


@router.get("/recommend-clustering", response_model=List[str])
async def recommend_tracks_clustering(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    playlist_name: str = Query(..., description="Playlist name to base recommendations on"),
    k: int = 10,
    n_neighbors: int = 5,
):
    """
    Recommend tracks for a given playlist name.
    """
    AuthController.protected_endpoint(credentials)
    return await clustering_service.recommend_tracks(playlist_name, k, n_neighbors)


@router.get("/recommend-collaborative", response_model=List[str])
async def recommend_tracks_collaborative(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    query_uris: List[str] = Query(..., description="List of seed track URIs"),
    k: int = 10,
):
    """
    Recommend tracks for a given playlist name.
    """
    AuthController.protected_endpoint(credentials)
    return await collaborative_service.recommend_tracks(query_uris=query_uris, k=k)


@router.get("/recommend-hybrid", response_model=List[str])
async def recommend_tracks_hybrid(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    playlist_name: str = Query(..., description="Playlist name to base recommendations on"),
    query_uris: List[str] = Query(..., description="List of seed track URIs"),
    k: int = 10,
    n_neighbors: int = 5,
):
    """
    Recommend tracks using a hybrid approach combining clustering and collaborative filtering.
    """
    AuthController.protected_endpoint(credentials)

    collaborative_recommendations = await collaborative_service.recommend_tracks(query_uris=query_uris, k=k)

    logger.info(
        f"Collaborative returned {
            len(collaborative_recommendations)} tracks")

    if len(collaborative_recommendations) >= k:
        return list(dict.fromkeys(collaborative_recommendations))[:k]

    remaining_num = k - len(collaborative_recommendations)

    clustering_recommendations = await clustering_service.recommend_tracks(playlist_name, remaining_num, n_neighbors)

    logger.info(
        f"Qdrant fallback returned {
            len(clustering_recommendations)} tracks")

    combined = list(
        dict.fromkeys(
            collaborative_recommendations +
            clustering_recommendations))

    print(f"Combined recommendations: {combined}")
    logger.info(
        f"Combined recommendations: {combined}")

    return combined[:k]
