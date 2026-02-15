from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import engine, Base

# Routers
from app.routers.auth import router as auth_router
from app.routers.posts import router as posts_router
from app.routers.transactions import router as tx_router
from app.routers.ratings import router as ratings_router
from app.routers.chat import router as chat_router  

import app.models 


app = FastAPI(title="Campus Marketplace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(tx_router)
app.include_router(ratings_router)
app.include_router(chat_router)  
