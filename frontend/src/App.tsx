import { useKeycloak } from './KeycloakProvider';
import {
  Button,
  Container,
  Typography,
  Box,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import SpotifyProfile from './components/spotify/SpotifyProfile';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function App() {
  const { keycloak, authenticated, loading } = useKeycloak();

  if (loading) return <Typography variant="h6" align="center">Loading...</Typography>;

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container
        maxWidth={false}
        disableGutters
        sx={{
          mt: 6,
          px: { xs: 2, sm: 4, md: 6 },
          width: '100%',
          maxWidth: {
            xs: '100%',     // full width on phones
            sm: '100%',     // full width on small tablets
            md: '1200px',   // mid-size width on medium screens
            lg: '1400px',   // wider on desktops
            xl: '1600px',   // max width on large desktops
          },
          mx: 'auto',
        }}
      >
        <Typography variant="h3" gutterBottom align="center">
          🎵 Conseillify
        </Typography>

        {authenticated ? (
          <>
            <Typography variant="h5" align="center" gutterBottom>
              Welcome back, {keycloak.tokenParsed?.given_name || 'friend'}!
            </Typography>

            <Box display="flex" justifyContent="center" mb={3}>
              <Button
                variant="contained"
                color="secondary"
                onClick={() => keycloak.logout({ redirectUri: window.location.origin })}
              >
                Logout
              </Button>
            </Box>

            <SpotifyProfile />
          </>
        ) : (
          <>
            <Typography variant="h6" align="center" paragraph>
              Welcome to your personalized Spotify dashboard. Log in or register to explore your music profile and recommendations.
            </Typography>

            <Box display="flex" justifyContent="center" gap={2}>
              <Button variant="contained" color="primary" onClick={() => keycloak.login()}>
                Login
              </Button>
              <Button variant="contained" color="secondary" onClick={() => keycloak.register()}>
                Register
              </Button>
            </Box>
          </>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;
