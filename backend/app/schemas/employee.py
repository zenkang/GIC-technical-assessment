import uuid
import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


class EmployeeCreate(BaseModel):
    name: str
    email_address: EmailStr
    phone_number: str
    gender: str
    cafe_id: Optional[uuid.UUID] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.fullmatch(r"[89]\d{7}", v):
            raise ValueError("Phone number must start with 8 or 9 and be exactly 8 digits")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ("Male", "Female"):
            raise ValueError("Gender must be Male or Female")
        return v


class EmployeeUpdate(BaseModel):
    name: str
    email_address: EmailStr
    phone_number: str
    gender: str
    cafe_id: Optional[uuid.UUID] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.fullmatch(r"[89]\d{7}", v):
            raise ValueError("Phone number must start with 8 or 9 and be exactly 8 digits")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ("Male", "Female"):
            raise ValueError("Gender must be Male or Female")
        return v


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email_address: str
    phone_number: str
    gender: str
    days_worked: int
    cafe: str  # cafe name, or empty string if unassigned
