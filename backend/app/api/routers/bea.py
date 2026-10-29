from fastapi import APIRouter

from app.clients.bea_client import BeaClient

router = APIRouter(
    prefix="/bea",
    tags=["BEA"]
)


@router.get("/gdp")
def get_gdp():

    return BeaClient.get_gdp()