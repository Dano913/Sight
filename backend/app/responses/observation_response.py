from datetime import date

from pydantic import BaseModel

class ObservationResponse(BaseModel):

    date: date

    value: float
    
    source: str