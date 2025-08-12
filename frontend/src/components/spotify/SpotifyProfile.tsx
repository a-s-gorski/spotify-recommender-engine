import { useEffect, useState } from "react";
import {
  Container,
  Typography,
  Button,
  Box,
  CssBaseline,
  createTheme,
  ThemeProvider,
  Alert,
} from "@mui/material";
import { redirectToAuthCodeFlow, getAccessToken } from "./authCodeWithPkce";
import RecommendationInterface from "../recommend/RecommendationInterface";
import ProfileHeader from "./ProfileHeader";
import TrackList from "./TrackList";
import PlaylistCreator from "./PlaylistCreator";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
  },
});

const clientId = import.meta.env.VITE_SPOTIFY_CLIENT_ID;

export default function SpotifyProfile() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [recentlyPlayed, setRecentlyPlayed] = useState<RecentlyPlayedTrack[]>([]);
  const [recommendedTracks, setRecommendedTracks] = useState<RecentlyPlayedTrack[]>([]);
  const [playlistTitle, setPlaylistTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);


  useEffect(() => {
    async function tryFetchProfile() {
      const token = localStorage.getItem("spotify_access_token");
      if (token) {
        setLoading(true);
        try {
          const profileData = await fetchProfile(token);
          setProfile(profileData);
          const history = await fetchRecentlyPlayed(token);
          setRecentlyPlayed(history);
          setError(null);
        } catch (e) {
          console.warn("Stored token invalid or expired, clearing it", e);
          localStorage.removeItem("spotify_access_token");
          setProfile(null);
        } finally {
          setLoading(false);
        }
      } else {
        const params = new URLSearchParams(window.location.search);
        const code = params.get("code");
        if (code) {
          setLoading(true);
          try {
            const accessToken = await getAccessToken(clientId, code);
            localStorage.setItem("spotify_access_token", accessToken);
            window.history.replaceState({}, document.title, window.location.pathname);
            const profileData = await fetchProfile(accessToken);
            const history = await fetchRecentlyPlayed(accessToken);
            setProfile(profileData);
            setRecentlyPlayed(history);
            setError(null);
          } catch (err) {
            console.error("Failed to get access token or fetch profile", err);
            setError("Authentication failed. Please try again.");
          } finally {
            setLoading(false);
          }
        }
      }
    }

    tryFetchProfile();
  }, []);

  async function fetchProfile(token: string): Promise<UserProfile> {
    const response = await fetch("https://api.spotify.com/v1/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error(`Failed to fetch profile: ${response.status}`);
    return response.json();
  }

  async function fetchRecentlyPlayed(token: string, limit: number = 50): Promise<RecentlyPlayedTrack[]> {
    const response = await fetch(`https://api.spotify.com/v1/me/player/recently-played?limit=${limit}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error(`Failed to fetch history: ${response.status}`);
    const data = await response.json();
    const seen = new Set();
    return data.items
      .filter((item: any) => {
        const uri = item.track.uri;
        if (seen.has(uri)) return false;
        seen.add(uri);
        return true;
      })
      .map((item: any) => ({
        trackUri: item.track.uri,
        albumImage: item.track.album.images?.[0]?.url ?? null,
        albumName: item.track.album.name,
        artistName: item.track.artists.map((a: any) => a.name).join(", "),
        trackName: item.track.name,
      }));
  }

  async function fetchTrackMetadata(uris: string[], token: string): Promise<RecentlyPlayedTrack[]> {
    if (!uris.length) return [];
    const ids = uris.map(uri => uri.split(":").pop()).join(",");
    const response = await fetch(`https://api.spotify.com/v1/tracks?ids=${ids}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error("Failed to fetch track metadata");
    const data = await response.json();
    return data.tracks.map((track: any) => ({
      trackUri: track.uri,
      albumImage: track.album.images?.[0]?.url ?? null,
      albumName: track.album.name,
      artistName: track.artists.map((a: any) => a.name).join(", "),
      trackName: track.name,
    }));
  }

  async function handleRecommendations(uris: string[]) {
    if (!uris.length) return;
    const token = localStorage.getItem("spotify_access_token");
    if (!token) return;
    try {
      const metadata = await fetchTrackMetadata(uris, token);
      setRecommendedTracks(metadata);
    } catch (err) {
      console.error("Failed to fetch metadata for recommendations:", err);
    }
  }

  async function createPlaylist() {
    const token = localStorage.getItem("spotify_access_token");
    if (!token || !playlistTitle || !recommendedTracks.length || !profile?.id) return;
    try {
      const createResponse = await fetch(`https://api.spotify.com/v1/users/${profile.id}/playlists`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: playlistTitle, public: false }),
      });
      if (!createResponse.ok) throw new Error("Failed to create playlist");
      const playlist = await createResponse.json();
      const uris = recommendedTracks.map(track => track.trackUri);
      const addResponse = await fetch(`https://api.spotify.com/v1/playlists/${playlist.id}/tracks`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ uris }),
      });
      if (!addResponse.ok) throw new Error("Failed to add tracks");
      alert("Playlist created successfully!");
      setPlaylistTitle("");
    } catch (error) {
      console.error("Playlist creation failed:", error);
    }
  }

  function handleLogout() {
    localStorage.removeItem("spotify_access_token");
    setProfile(null);
    setError(null);
  }

  if (loading) {
    return (
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <Container maxWidth="sm" sx={{ mt: 6 }}>
          <Typography variant="h6" align="center">Loading...</Typography>
        </Container>
      </ThemeProvider>
    );
  }

  if (error || !profile) {
    return (
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <Container maxWidth="sm" sx={{ mt: 6 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error || "You must be logged in to view your Spotify profile."}
          </Alert>
          <Box display="flex" justifyContent="center">
            <Button variant="contained" color="primary" onClick={() => redirectToAuthCodeFlow(clientId)}>
              Login with Spotify
            </Button>
          </Box>
        </Container>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ mt: 6 }}>
        <ProfileHeader profile={profile} />

        <Box my={4}>
          <TrackList title="Recently Played Tracks" tracks={recentlyPlayed} />
        </Box>

        {recentlyPlayed.length > 0 && (
          <Box my={4}>
            <RecommendationInterface
              trackUris={recentlyPlayed.map(track => track.trackUri)}
              onRecommendationsReceived={handleRecommendations}
            />
          </Box>
        )}

        {recommendedTracks.length > 0 && (
          <Box my={4}>
            <TrackList title="Recommended Tracks" tracks={recommendedTracks}  />
            <PlaylistCreator
              playlistTitle={playlistTitle}
              setPlaylistTitle={setPlaylistTitle}
              createPlaylist={createPlaylist}
            />
          </Box>
        )}

        <Box mt={5} display="flex" justifyContent="center">
          <Button variant="outlined" color="secondary" onClick={handleLogout}>
            Logout from Spotify
          </Button>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
