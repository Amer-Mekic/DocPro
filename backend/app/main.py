from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import documents

app = FastAPI(
    title="Smart Document Processing System",
    description="Upload and process business documents",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://doc-pro-pink.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
