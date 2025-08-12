from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from src.recommend.router import router as recommend_router

frontend_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")

app = FastAPI()

# app.include_router(auth_router)
app.include_router(recommend_router)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    frontend_url,
    "http://frontend:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check():
    return JSONResponse(content={"status": "ok"})
