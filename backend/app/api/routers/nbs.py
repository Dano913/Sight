from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.clients.nbs_client import NbsClient

router = APIRouter(
    prefix="/nbs",
    tags=["NBS"],
)


@router.get("/cpi")
def get_cpi():
    try:
        return NbsClient.get_cpi()
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


@router.get("/gdp")
def get_gdp():
    try:
        return NbsClient.get_gdp()
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


@router.get("/unemployment")
def get_unemployment():
    try:
        return NbsClient.get_unemployment()
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


@router.get("/inflation")
def get_inflation():
    try:
        return NbsClient.get_inflation()
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
