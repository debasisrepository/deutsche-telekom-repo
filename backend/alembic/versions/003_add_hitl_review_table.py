"""add_hitl_review_table

Revision ID: 003
Revises: 002
Create Date: 2026-11-12

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: str | None = '002'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create hitl_review table
    op.create_table(
        'hitl_review',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('review_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('assigned_role', sa.String(length=50), nullable=True),
        sa.Column('decision', sa.String(length=50), nullable=True),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('generated_payload', sa.Text(), nullable=True),
        sa.Column('final_payload', sa.Text(), nullable=True),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    with op.batch_alter_table('hitl_review', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_hitl_review_case_id'), ['case_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_hitl_review_review_type'), ['review_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_hitl_review_status'), ['status'], unique=False)
        batch_op.create_index(batch_op.f('ix_hitl_review_reviewer_id'), ['reviewer_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_hitl_review_created_at'), ['created_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('hitl_review', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_hitl_review_created_at'))
        batch_op.drop_index(batch_op.f('ix_hitl_review_reviewer_id'))
        batch_op.drop_index(batch_op.f('ix_hitl_review_status'))
        batch_op.drop_index(batch_op.f('ix_hitl_review_review_type'))
        batch_op.drop_index(batch_op.f('ix_hitl_review_case_id'))
    
    op.drop_table('hitl_review')
