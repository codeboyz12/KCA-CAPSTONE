from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.lifespan import lifespan
from routers import health, metadata, predict, recommend, projects

app = FastAPI(
    title="KCA ML Engine API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in [
    health.router,
    metadata.router,
    predict.router,
    recommend.router,
    projects.router,
]:
    app.include_router(router)