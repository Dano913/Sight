from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.clients.bea_client import BeaClient

router = APIRouter(
    prefix="/bea",
    tags=["BEA"],
)


@router.get("/gdp")
def get_gdp():
    try:
        return BeaClient.get_gdp()
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=str(e),
        ) from e
