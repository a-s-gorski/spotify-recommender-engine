from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.auth.router import router as auth_router
from src.recommend.router import router as recommend_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(recommend_router)


@app.get("/health", tags=["System"])
async def health_check():
    return JSONResponse(content={"status": "ok"})
