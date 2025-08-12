import { Box, TextField, Button } from "@mui/material";

interface PlaylistCreatorProps {
  playlistTitle: string;
  setPlaylistTitle: (val: string) => void;
  createPlaylist: () => void;
}

export default function PlaylistCreator({
  playlistTitle,
  setPlaylistTitle,
  createPlaylist,
}: PlaylistCreatorProps) {
  return (
    <Box mt={3} display="flex" gap={2} flexWrap="wrap">
      <TextField
        label="Playlist Name"
        variant="outlined"
        value={playlistTitle}
        onChange={(e) => setPlaylistTitle(e.target.value)}
        size="small"
        sx={{ minWidth: 250 }}
      />
      <Button
        variant="contained"
        color="primary"
        onClick={createPlaylist}
        disabled={!playlistTitle.trim()}
      >
        Create Playlist
      </Button>
    </Box>
  );
}
