"""Initial baseline schema

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-08-30 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Tables are auto-created by app.core.database.init_db() in dev
    pass

def downgrade() -> None:
    pass
