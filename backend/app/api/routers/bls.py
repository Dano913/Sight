from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.clients.bls_client import BlsClient

router = APIRouter(
    prefix="/bls",
    tags=["BLS"],
)


@router.get("/inflation")
def get_inflation():
    try:
        return BlsClient.get_inflation()
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
        return BlsClient.get_unemployment()
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
