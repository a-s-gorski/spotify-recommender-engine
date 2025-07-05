from fastapi import Depends, Form, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.models import TokenResponse, UserInfo
from src.auth.service import AuthService

# Initialize HTTPBearer security dependency
bearer_scheme = HTTPBearer()


class AuthController:
    """
    Controller for handling authentication logic.
    """

    @staticmethod
    def read_root():
        """
        Root endpoint providing basic information and documentation link.

        Returns:
            dict: A welcome message and link to the documentation.
        """
        return {
            "message": (
                "Welcome to the Keycloak authentication system. "
                "Use the /login endpoint to authenticate and /protected to access the protected resource."
            ),
            "documentation": "/docs",
        }

    @staticmethod
    def login(username: str = Form(...),
              password: str = Form(...)) -> TokenResponse:
        """
        Authenticate user and return access token.

        Args:
            username (str): The username of the user attempting to log in.
            password (str): The password of the user.

        Raises:
            HTTPException: If the authentication fails (wrong credentials).

        Returns:
            TokenResponse: Contains the access token upon successful authentication.
        """
        # Authenticate the user using the AuthService
        token = AuthService.authenticate_user(username, password)

        print(token.keys())

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        return TokenResponse(access_token=token["access_token"],
                             token_type=token["token_type"],
                             expires_in=token["expires_in"],
                             refresh_expires_in=token["refresh_expires_in"],
                             refresh_token=token["refresh_token"])

    @staticmethod
    def refresh_token(refresh_token: str = Form(...)) -> TokenResponse:
        """
        Refresh the access token using the provided refresh token.

        Args:
            refresh_token (str): The refresh token to use for obtaining a new access token.

        Raises:
            HTTPException: If the refresh token is invalid or not provided.

        Returns:
            TokenResponse: Contains the new access token and related information.
        """
        # Refresh the token using the AuthService
        new_token = AuthService.refresh_token(refresh_token)

        if not new_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        return TokenResponse(
            access_token=new_token["access_token"],
            token_type=new_token["token_type"],
            expires_in=new_token["expires_in"],
            refresh_expires_in=new_token["refresh_expires_in"],
            refresh_token=new_token["refresh_token"])

    @staticmethod
    def protected_endpoint(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    ) -> UserInfo:
        """
        Access a protected resource that requires valid token authentication.

        Args:
            credentials (HTTPAuthorizationCredentials): Bearer token provided via HTTP Authorization header.

        Raises:
            HTTPException: If the token is invalid or not provided.

        Returns:
            UserInfo: Information about the authenticated user.
        """
        # Extract the bearer token from the provided credentials
        token = credentials.credentials

        # Verify the token and get user information
        user_info = AuthService.verify_token(token)

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_info
