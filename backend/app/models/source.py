from pydantic import BaseModel


class Source(BaseModel):
    id: int
    code: str
    name: str