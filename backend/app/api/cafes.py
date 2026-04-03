"""
Cafe route handlers — HTTP layer only.

Each handler parses the request, builds a command/query,
and dispatches it via the Mediator. No DB logic here.
"""

import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.mediator import Mediator, get_mediator
from app.schemas import CafeResponse
from app.commands.cafe_commands import CreateCafeCommand, UpdateCafeCommand, DeleteCafeCommand
from app.queries.cafe_queries import GetCafesQuery

router = APIRouter(prefix="/cafes", tags=["cafes"])


@router.get("", response_model=List[CafeResponse])
async def list_cafes(
    location: Optional[str] = None,
    mediator: Mediator = Depends(lambda db=Depends(get_db): get_mediator(db)),
):
    #List all cafes, optionally filtered by location (case-insensitive).
    return await mediator.send(GetCafesQuery(location=location))


@router.post("", response_model=CafeResponse, status_code=201)
async def create_cafe(
    name: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    logo: Optional[UploadFile] = File(None),
    mediator: Mediator = Depends(lambda db=Depends(get_db): get_mediator(db)),
):
    #Create a new cafe. Logo is an optional.
    return await mediator.send(
        CreateCafeCommand(name=name, description=description, location=location, logo=logo)
    )


@router.put("/{cafe_id}", response_model=CafeResponse)
async def update_cafe(
    cafe_id: uuid.UUID,
    name: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    logo: Optional[UploadFile] = File(None),
    mediator: Mediator = Depends(lambda db=Depends(get_db): get_mediator(db)),
):
    #Update an existing cafe. If a new logo is uploaded it replaces the old one.
    return await mediator.send(
        UpdateCafeCommand(
            cafe_id=cafe_id, name=name, description=description, location=location, logo=logo
        )
    )


@router.delete("/{cafe_id}")
async def delete_cafe(
    cafe_id: uuid.UUID,
    mediator: Mediator = Depends(lambda db=Depends(get_db): get_mediator(db)),
):
    #Delete a cafe and all its assigned employees.
    return await mediator.send(DeleteCafeCommand(cafe_id=cafe_id))
