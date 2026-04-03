"""
Employee route handlers — HTTP layer only.

Each handler parses the request, builds a command/query,
and dispatches it via the Mediator. No DB logic here.
"""

import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.mediator import Mediator, get_mediator
from app.schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.commands.employee_commands import (
    CreateEmployeeCommand,
    UpdateEmployeeCommand,
    DeleteEmployeeCommand,
)
from app.queries.employee_queries import GetEmployeesQuery

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=List[EmployeeResponse])
async def list_employees(
    cafe: Optional[str] = None,
    mediator: Mediator = Depends(lambda db=Depends(get_db): get_mediator(db)),
):
    #List all employees, optionally filtered by cafe ID. If cafe ID is provided but not found, returns an empty list.
    return await mediator.send(GetEmployeesQuery(cafe=cafe))


@router.post("", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    payload: EmployeeCreate,
    mediator: Mediator = Depends(lambda db=Depends(get_db): get_mediator(db)),
):
    #Create a new employee. Auto-generates the employee ID. assigns the employee to a cafe if cafe_id is provided.
    return await mediator.send(
        CreateEmployeeCommand(
            name=payload.name,
            email_address=str(payload.email_address),
            phone_number=payload.phone_number,
            gender=payload.gender,
            cafe_id=payload.cafe_id,
        )
    )


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    payload: EmployeeUpdate,
    mediator: Mediator = Depends(lambda db=Depends(get_db): get_mediator(db)),
):
    #Update an existing employee. If cafe_id is provided, reassign the employee to that cafe.
    return await mediator.send(
        UpdateEmployeeCommand(
            employee_id=employee_id,
            name=payload.name,
            email_address=str(payload.email_address),
            phone_number=payload.phone_number,
            gender=payload.gender,
            cafe_id=payload.cafe_id,
        )
    )


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: str,
    mediator: Mediator = Depends(lambda db=Depends(get_db): get_mediator(db)),
):
    #Delete an existing employee. The cafe_employees assignment is cascade-deleted.
    return await mediator.send(DeleteEmployeeCommand(employee_id=employee_id))
