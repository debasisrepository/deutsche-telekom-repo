"""add vms_handoff table

Revision ID: 005
Revises: 004
Create Date: 2026-11-12

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: str | None = '004'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create vms_handoff table for single-resource case routing."""
    op.create_table(
        'vms_handoff',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('vms_reference_id', sa.String(length=100), nullable=False),
        sa.Column('handoff_status', sa.String(length=50), nullable=False),
        sa.Column('request_snapshot', sa.Text(), nullable=False),
        sa.Column('handed_off_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('requirement_tags', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
        sa.UniqueConstraint('case_id')
    )


def downgrade() -> None:
    """Drop vms_handoff table."""
    op.drop_table('vms_handoff')
