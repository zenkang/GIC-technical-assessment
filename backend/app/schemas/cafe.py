import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CafeCreate(BaseModel):
    name: str
    description: str
    location: str
    # logo is handled as an UploadFile in the route


class CafeUpdate(BaseModel):
    name: str
    description: str
    location: str


class CafeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str
    employees: int
    logo: Optional[str] = None
    location: str
