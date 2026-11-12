"""add evidence tables

Revision ID: 006
Revises: 005
Create Date: 2026-11-12

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: str | None = '005'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create evidence-related tables for supplier knowledge base."""
    # Create supplier table
    op.create_table(
        'supplier',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('supplier_code', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('contact_endpoint', sa.Text(), nullable=True),
        sa.Column('evidence_source_status', sa.String(length=50), nullable=True),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('supplier_code')
    )
    op.create_index(op.f('ix_supplier_supplier_code'), 'supplier', ['supplier_code'], unique=True)

    # Create historical_order table
    op.create_table(
        'historical_order',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_order_id', sa.String(length=100), nullable=False),
        sa.Column('service_domain', sa.String(length=100), nullable=False),
        sa.Column('completion_date', sa.Date(), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_order_id')
    )
    op.create_index(op.f('ix_historical_order_external_order_id'), 'historical_order', ['external_order_id'], unique=True)

    # Create commissioned_sow table
    op.create_table(
        'commissioned_sow',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_sow_id', sa.String(length=100), nullable=False),
        sa.Column('scope_summary', sa.Text(), nullable=False),
        sa.Column('signed_date', sa.Date(), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_sow_id')
    )
    op.create_index(op.f('ix_commissioned_sow_external_sow_id'), 'commissioned_sow', ['external_sow_id'], unique=True)

    # Create case_evidence table
    op.create_table(
        'case_evidence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('historical_order_id', sa.Integer(), nullable=True),
        sa.Column('commissioned_sow_id', sa.Integer(), nullable=True),
        sa.Column('citation_label', sa.Text(), nullable=False),
        sa.Column('citation_ref', sa.Text(), nullable=False),
        sa.Column('evidence_summary', sa.Text(), nullable=False),
        sa.Column('evidence_found', sa.Boolean(), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['supplier.id'], ),
        sa.ForeignKeyConstraint(['historical_order_id'], ['historical_order.id'], ),
        sa.ForeignKeyConstraint(['commissioned_sow_id'], ['commissioned_sow.id'], )
    )
    op.create_index(op.f('ix_case_evidence_case_id'), 'case_evidence', ['case_id'], unique=False)
    op.create_index(op.f('ix_case_evidence_supplier_id'), 'case_evidence', ['supplier_id'], unique=False)

    # Create supplier_citation table (prepared for future longlist implementation)
    # Note: proposal_supplier_id FK will be added when proposal_supplier table is created
    op.create_table(
        'supplier_citation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('proposal_supplier_id', sa.Integer(), nullable=False),
        sa.Column('case_evidence_id', sa.Integer(), nullable=False),
        sa.Column('citation_type', sa.String(length=50), nullable=False),
        sa.Column('citation_ref', sa.Text(), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['case_evidence_id'], ['case_evidence.id'], name='fk_supplier_citation_case_evidence')
    )
    op.create_index(op.f('ix_supplier_citation_proposal_supplier_id'), 'supplier_citation', ['proposal_supplier_id'], unique=False)
    op.create_index(op.f('ix_supplier_citation_case_evidence_id'), 'supplier_citation', ['case_evidence_id'], unique=False)


def downgrade() -> None:
    """Drop evidence-related tables."""
    op.drop_index(op.f('ix_supplier_citation_case_evidence_id'), table_name='supplier_citation')
    op.drop_index(op.f('ix_supplier_citation_proposal_supplier_id'), table_name='supplier_citation')
    op.drop_table('supplier_citation')
    
    op.drop_index(op.f('ix_case_evidence_supplier_id'), table_name='case_evidence')
    op.drop_index(op.f('ix_case_evidence_case_id'), table_name='case_evidence')
    op.drop_table('case_evidence')
    
    op.drop_index(op.f('ix_commissioned_sow_external_sow_id'), table_name='commissioned_sow')
    op.drop_table('commissioned_sow')
    
    op.drop_index(op.f('ix_historical_order_external_order_id'), table_name='historical_order')
    op.drop_table('historical_order')
    
    op.drop_index(op.f('ix_supplier_supplier_code'), table_name='supplier')
    op.drop_table('supplier')
