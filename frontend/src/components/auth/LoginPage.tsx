import { useState } from 'react';
import { Box, Button, TextField, Typography } from '@mui/material';
import { useAuth } from '../../AuthProvider';

export default function LoginPage({ onBack }: { onBack: () => void }) {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async () => {
    const success = await login(username, password);
    if (!success) setError('Invalid credentials');
  };

  return (
    <Box>
      <Typography variant="h5" align="center" gutterBottom>Login</Typography>
      <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
        <TextField label="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <TextField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        {error && <Typography color="error">{error}</Typography>}
        <Button variant="contained" color="primary" onClick={handleLogin}>Login</Button>
        <Button onClick={onBack}>Back</Button>
      </Box>
    </Box>
  );
}
