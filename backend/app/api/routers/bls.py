from fastapi import APIRouter

from app.clients.bls_client import BlsClient

router = APIRouter(
    prefix="/bls",
    tags=["BLS"]
)


@router.get("/inflation")
def get_inflation():

    return BlsClient.get_inflation()

@router.get("/unemployment")
def get_unemployment():
    return BlsClient.get_unemployment()