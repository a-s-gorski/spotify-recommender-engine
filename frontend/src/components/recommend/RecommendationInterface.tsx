import React, { useState } from "react";
import { Box, Typography } from "@mui/material";
import { useKeycloak } from "../../KeycloakProvider";
import PlaylistNameInput from "./PlaylistNameInput";
import StrategySelector from "./StrategySelector";
import RecommendationSlider from "./RecommendationSlider";
import FetchButton from "./FetchButton";

const backendUrl: string = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

interface Props {
    trackUris: string[];
    onRecommendationsReceived: (uris: string[]) => void;
}

export default function RecommendationInterface({ trackUris, onRecommendationsReceived }: Props) {
    const { keycloak, authenticated, loading } = useKeycloak();
    const [playlistName, setPlaylistName] = useState("");
    const [recommendationLimit, setRecommendationLimit] = useState(10);
    const [recommendationStrategy, setRecommendationStrategy] = useState("hybrid");
    const [loadingRecs, setLoadingRecs] = useState(false);

    const maxRecommendations = Math.max(trackUris.length, 1);

    const fetchRecommendations = async () => {
        setLoadingRecs(true);
        try {
            await keycloak.updateToken(30);

            const params = new URLSearchParams();

            const isClustering = recommendationStrategy === "clustering";
            const isCollaborative = recommendationStrategy === "collaborative";
            const isHybrid = recommendationStrategy === "hybrid";

            if (isClustering || isHybrid) {
                params.append("playlist_name", playlistName);
            }

            if (!isClustering) {
                trackUris.forEach(uri => params.append("query_uris", uri));
            }

            params.append("k", recommendationLimit.toString());

            if (isClustering || isHybrid) {
                params.append("n_neighbors", "10");
            }

            const endpointMap = {
                clustering: `${backendUrl}/recommend/recommend-clustering`,
                collaborative: `${backendUrl}/recommend/recommend-collaborative`,
                hybrid: `${backendUrl}/recommend/recommend-hybrid`,
            };

            const endpoint = endpointMap[recommendationStrategy as keyof typeof endpointMap];

            const response = await fetch(`${endpoint}?${params.toString()}`, {
                headers: {
                    Authorization: `Bearer ${keycloak.token}`,
                },
            });

            if (!response.ok) throw new Error(`Failed to fetch from ${endpoint}`);

            const uris: string[] = await response.json();
            onRecommendationsReceived(uris);
        } catch (err) {
            console.error("Recommendation fetch failed", err);
        } finally {
            setLoadingRecs(false);
        }
    };

    if (loading) return <Typography>Loading...</Typography>;

    return (
        <Box mt={4}>
            <Typography variant="h6" gutterBottom>
                Generate Recommendations
            </Typography>

            {authenticated ? (
                <>
                    <PlaylistNameInput value={playlistName} onChange={setPlaylistName} />
                    <StrategySelector value={recommendationStrategy} onChange={setRecommendationStrategy} />
                    <RecommendationSlider
                        value={recommendationLimit}
                        onChange={setRecommendationLimit}
                        max={maxRecommendations}
                    />
                    <FetchButton
                        loading={loadingRecs}
                        disabled={!trackUris.length}
                        onClick={fetchRecommendations}
                    />
                </>
            ) : (
                <Typography color="textSecondary">Please log in to see recommendations.</Typography>
            )}
        </Box>
    );
}
