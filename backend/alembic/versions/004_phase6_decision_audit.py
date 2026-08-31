"""Phase 6 Decision Workflow & Tamper-Evident Audit Migration

Revision ID: 004_phase6_decision_audit
Revises: 003_phase5_policy_rag
Create Date: 2026-08-30 10:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_phase6_decision_audit'
down_revision: Union[str, None] = '003_phase5_policy_rag'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
