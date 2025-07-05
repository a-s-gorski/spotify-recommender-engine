from fastapi import APIRouter, Depends, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.controller import AuthController
from src.auth.models import TokenResponse, UserInfo

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()


@router.get("/")
async def read_root():
    return AuthController.read_root()


@router.post("/login", response_model=TokenResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    return AuthController.login(username, password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str = Form(...)):
    return AuthController.refresh_token(refresh_token)


@router.get("/protected", response_model=UserInfo)
async def protected_endpoint(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    return AuthController.protected_endpoint(credentials)
