"""Add mapping and longlist tables

Revision ID: 007
Revises: 006
Create Date: 2026-11-12

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: str | None = '006'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create panel table
    op.create_table(
        'panel',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('panel_code', sa.String(length=50), nullable=False),
        sa.Column('panel_name', sa.String(length=255), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_panel_panel_code', 'panel', ['panel_code'], unique=True)
    
    # Create functional_group table
    op.create_table(
        'functional_group',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('functional_group_code', sa.String(length=50), nullable=False),
        sa.Column('functional_group_name', sa.String(length=255), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_functional_group_functional_group_code', 'functional_group', ['functional_group_code'], unique=True)
    
    # Create case_mapping table
    op.create_table(
        'case_mapping',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('panel_id', sa.Integer(), nullable=False),
        sa.Column('functional_group_id', sa.Integer(), nullable=False),
        sa.Column('mapping_status', sa.String(length=50), nullable=False),
        sa.Column('rationale_inputs', sa.Text(), nullable=True),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
        sa.ForeignKeyConstraint(['panel_id'], ['panel.id'], ),
        sa.ForeignKeyConstraint(['functional_group_id'], ['functional_group.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_case_mapping_case_id', 'case_mapping', ['case_id'], unique=False)
    op.create_index('ix_case_mapping_panel_id', 'case_mapping', ['panel_id'], unique=False)
    op.create_index('ix_case_mapping_functional_group_id', 'case_mapping', ['functional_group_id'], unique=False)
    
    # Create longlist_proposal table
    op.create_table(
        'longlist_proposal',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('version_no', sa.Integer(), nullable=False),
        sa.Column('proposal_status', sa.String(length=50), nullable=False),
        sa.Column('generation_inputs', sa.Text(), nullable=True),
        sa.Column('generated_by_agent_run_id', sa.String(length=100), nullable=True),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_longlist_proposal_case_id', 'longlist_proposal', ['case_id'], unique=False)
    
    # Create proposal_supplier table
    op.create_table(
        'proposal_supplier',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('proposal_id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('rank_position', sa.Integer(), nullable=False),
        sa.Column('recommendation_status', sa.String(length=50), nullable=False),
        sa.Column('ranking_score', sa.Float(), nullable=False),
        sa.Column('citation_complete', sa.Boolean(), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['proposal_id'], ['longlist_proposal.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['supplier.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_proposal_supplier_proposal_id', 'proposal_supplier', ['proposal_id'], unique=False)
    op.create_index('ix_proposal_supplier_supplier_id', 'proposal_supplier', ['supplier_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_proposal_supplier_supplier_id', table_name='proposal_supplier')
    op.drop_index('ix_proposal_supplier_proposal_id', table_name='proposal_supplier')
    op.drop_table('proposal_supplier')
    
    op.drop_index('ix_longlist_proposal_case_id', table_name='longlist_proposal')
    op.drop_table('longlist_proposal')
    
    op.drop_index('ix_case_mapping_functional_group_id', table_name='case_mapping')
    op.drop_index('ix_case_mapping_panel_id', table_name='case_mapping')
    op.drop_index('ix_case_mapping_case_id', table_name='case_mapping')
    op.drop_table('case_mapping')
    
    op.drop_index('ix_functional_group_functional_group_code', table_name='functional_group')
    op.drop_table('functional_group')
    
    op.drop_index('ix_panel_panel_code', table_name='panel')
    op.drop_table('panel')
