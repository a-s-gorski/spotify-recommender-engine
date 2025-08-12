import { useState } from 'react';
import { Box, Button, TextField, Typography } from '@mui/material';
import { useAuth } from '../../AuthProvider';

export default function RegisterPage({ onBack }: { onBack: () => void }) {
  const { register } = useAuth();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleRegister = async () => {
    const ok = await register(username, email, password);
    if (ok) setSuccess(true);
    else setError('Registration failed');
  };

  return (
    <Box>
      <Typography variant="h5" align="center" gutterBottom>Register</Typography>
      <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
        <TextField label="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <TextField label="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <TextField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        {success && <Typography color="success.main">Registration successful!</Typography>}
        {error && <Typography color="error">{error}</Typography>}
        <Button variant="contained" color="secondary" onClick={handleRegister}>Register</Button>
        <Button onClick={onBack}>Back</Button>
      </Box>
    </Box>
  );
}
