import uuid
from datetime import date
from sqlalchemy import String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base


class Employee(Base):
    __tablename__ = "employees"

    # Format: UIXXXXXXX (UI + 7 alphanumeric chars), auto-generated
    id: Mapped[str] = mapped_column(String(9), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email_address: Mapped[str] = mapped_column(String(320), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(8), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)

    # UNIQUE on CafeEmployee.employee_id enforces one-cafe-per-employee at DB level
    assignment: Mapped["CafeEmployee | None"] = relationship(  # noqa: F821
        "CafeEmployee", back_populates="employee", cascade="all, delete-orphan", uselist=False
    )


class CafeEmployee(Base):
    __tablename__ = "cafe_employees"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    cafe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cafes.id", ondelete="CASCADE"), nullable=False
    )
    employee_id: Mapped[str] = mapped_column(
        String(9), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)

    cafe: Mapped["Cafe"] = relationship("Cafe", back_populates="assignments")  # noqa: F821
    employee: Mapped["Employee"] = relationship("Employee", back_populates="assignment")

    __table_args__ = (
        UniqueConstraint("employee_id", name="uq_cafe_employees_employee_id"),
    )
