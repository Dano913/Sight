from contextlib import asynccontextmanager

from pathlib import Path
from dotenv import load_dotenv
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.api.routers.health import router as health_router
from app.api.routers.regions import router as regions_router
from app.api.routers.indicators import router as indicators_router
from app.api.routers.observations import router as observations_router
from app.api.routers.sources import router as sources_router
from app.api.routers.bea import router as bea_router
from app.api.routers.bls import router as bls_router
from app.api.routers.nbs import router as nbs_router
from app.api.routers.query import router as query_router
from app.api.routers.analysis import router as analysis_router
from app.api.routers.investment import router as investment_router


from app.repositories.observation_repository import ObservationRepository


@asynccontextmanager
async def lifespan(app: FastAPI):

    ObservationRepository.create_table()

    yield


app = FastAPI(
    title="MacroAtlas API",
    version="0.1.0",
    description="API para el análisis de indicadores macroeconómicos.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(regions_router)
app.include_router(indicators_router)
app.include_router(observations_router)
app.include_router(sources_router)
app.include_router(bea_router)
app.include_router(bls_router)
app.include_router(nbs_router)
app.include_router(query_router)
app.include_router(analysis_router)
app.include_router(investment_router)