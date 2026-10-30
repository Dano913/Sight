from __future__ import annotations

from .analysis import router as analysis_router
from .bea import router as bea_router
from .bls import router as bls_router
from .health import router as health_router
from .indicators import router as indicators_router
from .investment import router as investment_router
from .nbs import router as nbs_router
from .observations import router as observations_router
from .query import router as query_router
from .regions import router as regions_router
from .sources import router as sources_router

__all__ = [
    "analysis_router",
    "bea_router",
    "bls_router",
    "health_router",
    "indicators_router",
    "investment_router",
    "nbs_router",
    "observations_router",
    "query_router",
    "regions_router",
    "sources_router",
]
