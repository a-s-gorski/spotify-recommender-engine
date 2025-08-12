import { useState } from "react";
import { Box, Typography } from "@mui/material";
import { useAuth } from "../../AuthProvider";
import PlaylistNameInput from "./PlaylistNameInput";
import StrategySelector from "./StrategySelector";
import RecommendationSlider from "./RecommendationSlider";
import FetchButton from "./FetchButton";

const backendUrl: string = import.meta.env.VITE_BACKEND_URL || "http://localhost:8080";

interface Props {
  trackUris: string[];
  onRecommendationsReceived: (uris: string[]) => void;
}

export default function RecommendationInterface({ trackUris, onRecommendationsReceived }: Props) {
  const { authFetch } = useAuth();
  const [playlistName, setPlaylistName] = useState("");
  const [recommendationLimit, setRecommendationLimit] = useState(10);
  const [recommendationStrategy, setRecommendationStrategy] = useState("hybrid");
  const [loadingRecs, setLoadingRecs] = useState(false);

  const maxRecommendations = Math.max(trackUris.length, 1);

  const fetchRecommendations = async () => {
    setLoadingRecs(true);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000);

    try {
      const params = new URLSearchParams();

      const isClustering = recommendationStrategy === "clustering";
      const isHybrid = recommendationStrategy === "hybrid";

      if (isClustering || isHybrid) {
        params.append("playlistName", playlistName);
        params.append("nNeighbors", "10");
      }

      if (!isClustering) {
        trackUris.forEach(uri => {
          params.append("queryUris", uri);
        });
      }

      params.append("k", recommendationLimit.toString());

      const endpointMap = {
        clustering: `${backendUrl}/api/recommendations/clustering`,
        collaborative: `${backendUrl}/api/recommendations/collaborative`,
        hybrid: `${backendUrl}/api/recommendations/hybrid`,
      };

      const endpoint = endpointMap[recommendationStrategy as keyof typeof endpointMap];

      const response = await authFetch(`${endpoint}?${params.toString()}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        },
        signal: controller.signal,
      });

      if (!response.ok) throw new Error(`Failed to fetch from ${endpoint}`);

      const uris: string[] = await response.json();
      onRecommendationsReceived(uris);
    } catch (err) {
      if ((err as Error).name === "AbortError") {
        console.error("Recommendation fetch aborted due to timeout.");
      } else {
        console.error("Recommendation fetch failed", err);
      }
    } finally {
      clearTimeout(timeoutId);
      setLoadingRecs(false);
    }
  };

  return (
    <Box mt={4}>
      <Typography variant="h6" gutterBottom>
        Generate Recommendations
      </Typography>

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
    </Box>
  );
}
