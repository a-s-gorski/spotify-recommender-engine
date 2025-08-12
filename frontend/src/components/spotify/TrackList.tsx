import {
  Typography,
  Card,
  CardContent,
  CardMedia,
  Box,
} from "@mui/material";

import Grid from "@mui/material/Grid";
import type { OverridableComponent } from "@mui/material/OverridableComponent";
import type { GridTypeMap } from "@mui/material/Grid";

interface Track {
  trackUri: string;
  albumImage: string | null;
  albumName: string;
  artistName: string;
  trackName: string;
}

// Type alias for Grid using default component "div"
const GridItem: OverridableComponent<GridTypeMap<{}, "div">> = Grid;

export default function TrackList({ title, tracks }: { title: string; tracks: Track[] }) {
  return (
    <Box>
      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
        {title}
      </Typography>
      <Grid container spacing={1}>
        {tracks.slice(0, 20).map((track) => (
          <GridItem
            // item
            // xs={6}
            // sm={4}
            // md={2}
            sx={{ flexBasis: "12.5%", maxWidth: "12.5%" }}
            key={track.trackUri}
          >
            <Card
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                bgcolor: "background.paper",
                p: 0.5,
              }}
            >
              {track.albumImage && (
                <CardMedia
                  component="img"
                  height="60"
                  image={track.albumImage}
                  alt={track.albumName}
                  sx={{ objectFit: "cover" }}
                />
              )}
              <CardContent sx={{ p: 0.5 }}>
                <Typography variant="caption" fontWeight="bold" noWrap>
                  {track.trackName}
                </Typography>
                <Typography variant="caption" color="text.secondary" noWrap>
                  {track.artistName}
                </Typography>
                <Typography variant="caption" color="text.secondary" noWrap>
                  {track.albumName}
                </Typography>
              </CardContent>
            </Card>
          </GridItem>
        ))}
      </Grid>
    </Box>
  );
}
