from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import engine, Base
from app.routers.posts import router as posts_router
from app.routers.transactions import router as tx_router
from app.routers.ratings import router as ratings_router
from app.routers.users import router as user_router


app.include_router(users.router)

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


app.include_router(posts_router)
app.include_router(tx_router)
app.include_router(ratings_router)
app.include_router(users_router)
