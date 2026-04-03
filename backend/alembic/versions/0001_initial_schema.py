"""initial schema

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cafes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("logo", sa.String(500), nullable=True),
        sa.Column("location", sa.String(255), nullable=False),
    )

    op.create_table(
        "employees",
        sa.Column("id", sa.String(9), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email_address", sa.String(320), nullable=False),
        sa.Column("phone_number", sa.String(8), nullable=False),
        sa.Column("gender", sa.String(10), nullable=False),
    )

    op.create_table(
        "cafe_employees",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "cafe_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cafes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "employee_id",
            sa.String(9),
            sa.ForeignKey("employees.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.UniqueConstraint("employee_id", name="uq_cafe_employees_employee_id"),
    )


def downgrade() -> None:
    op.drop_table("cafe_employees")
    op.drop_table("employees")
    op.drop_table("cafes")
