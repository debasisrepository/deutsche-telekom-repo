"""Add adjustment and validation tables

Revision ID: 008_add_adjustment_and_validation_tables
Revises: 007_add_mapping_and_longlist_tables
Create Date: 2026-11-12

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: str | None = '007'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create supplier_adjustment and policy_validation tables."""
    
    # Create supplier_adjustment table
    op.create_table(
        'supplier_adjustment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('change_type', sa.String(20), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('actor_id', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resulting_supplier_count', sa.Integer(), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['supplier.id'], ),
    )
    op.create_index(op.f('ix_supplier_adjustment_case_id'), 'supplier_adjustment', ['case_id'], unique=False)
    op.create_index(op.f('ix_supplier_adjustment_supplier_id'), 'supplier_adjustment', ['supplier_id'], unique=False)
    op.create_index(op.f('ix_supplier_adjustment_created_at'), 'supplier_adjustment', ['created_at'], unique=False)
    
    # Create policy_validation table
    op.create_table(
        'policy_validation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('validation_type', sa.String(50), nullable=False),
        sa.Column('supplier_count', sa.Integer(), nullable=False),
        sa.Column('validation_result', sa.String(50), nullable=False),
        sa.Column('rule_snapshot', sa.Text(), nullable=True),
        sa.Column('validated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
    )
    op.create_index(op.f('ix_policy_validation_case_id'), 'policy_validation', ['case_id'], unique=False)
    op.create_index(op.f('ix_policy_validation_validated_at'), 'policy_validation', ['validated_at'], unique=False)


def downgrade() -> None:
    """Drop supplier_adjustment and policy_validation tables."""
    op.drop_index(op.f('ix_policy_validation_validated_at'), table_name='policy_validation')
    op.drop_index(op.f('ix_policy_validation_case_id'), table_name='policy_validation')
    op.drop_table('policy_validation')
    
    op.drop_index(op.f('ix_supplier_adjustment_created_at'), table_name='supplier_adjustment')
    op.drop_index(op.f('ix_supplier_adjustment_supplier_id'), table_name='supplier_adjustment')
    op.drop_index(op.f('ix_supplier_adjustment_case_id'), table_name='supplier_adjustment')
    op.drop_table('supplier_adjustment')
