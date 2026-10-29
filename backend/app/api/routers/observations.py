from fastapi import APIRouter

from app.services.catalog.observation_service import ObservationService

router = APIRouter()


@router.get("/observations/{indicator_code}")
def get_observations(
    indicator_code: str,
    region: str | None = None,
):
    print(">>> ENTRANDO AL ROUTER", indicator_code, region)
    
    return ObservationService.get_observations(
        indicator_code,
        region,
    )