import { useAuth } from './AuthProvider';
import { Button, Container, Typography, Box, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import SpotifyProfile from './components/spotify/SpotifyProfile';
import { useState } from 'react';
import LoginPage from './components/auth/LoginPage';
import RegisterPage from './components/auth/RegisterPage';

const darkTheme = createTheme({ palette: { mode: 'dark' } });

function App() {
  const { accessToken, logout } = useAuth();
  const [mode, setMode] = useState<'home' | 'login' | 'register'>('home');

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth={false} disableGutters sx={{ mt: 6, px: 4, maxWidth: '1400px', mx: 'auto' }}>
        <Typography variant="h3" gutterBottom align="center">
          🎵 Conseillify
        </Typography>

        {accessToken ? (
          <>
            <Typography variant="h5" align="center" gutterBottom>
              Welcome back!
            </Typography>

            <Box display="flex" justifyContent="center" mb={3}>
              <Button variant="contained" color="secondary" onClick={logout}>
                Logout
              </Button>
            </Box>

            <SpotifyProfile />
          </>
        ) : mode === 'login' ? (
          <LoginPage onBack={() => setMode('home')} />
        ) : mode === 'register' ? (
          <RegisterPage onBack={() => setMode('home')} />
        ) : (
          <>
            <Typography variant="h6" align="center" paragraph>
              Welcome to your personalized Spotify dashboard. Log in or register to explore your music profile and recommendations.
            </Typography>
            <Box display="flex" justifyContent="center" gap={2}>
              <Button variant="contained" color="primary" onClick={() => setMode('login')}>
                Login
              </Button>
              <Button variant="contained" color="secondary" onClick={() => setMode('register')}>
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