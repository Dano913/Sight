from fastapi import APIRouter

from app.clients.nbs_client import NbsClient


router = APIRouter(
    prefix="/nbs",
    tags=["nbs"]
)


@router.get("/cpi")
def get_cpi():

    return NbsClient.get_cpi()



@router.get("/gdp")
def get_gdp():

    return NbsClient.get_gdp()



@router.get("/unemployment")
def get_unemployment():

    return NbsClient.get_unemployment()

@router.get("/inflation")
def get_inflation():

    return NbsClient.get_inflation()
