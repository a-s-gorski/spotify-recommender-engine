import { Avatar, Typography, Box } from "@mui/material";

interface ProfileHeaderProps {
  profile: UserProfile;
}

export default function ProfileHeader({ profile }: ProfileHeaderProps) {
  const profileImage = profile.images?.[0]?.url;

  return (
    <Box display="flex" alignItems="center" mb={4} gap={2}>
      {profileImage && (
        <Avatar
          alt={profile.display_name}
          src={profileImage}
          sx={{ width: 64, height: 64 }}
        />
      )}
      <Typography variant="h5" fontWeight="bold">
        Welcome, {profile.display_name}
      </Typography>
    </Box>
  );
}
