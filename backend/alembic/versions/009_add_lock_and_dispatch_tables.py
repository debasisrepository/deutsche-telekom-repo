"""add lock and dispatch tables

Revision ID: 009
Revises: 008
Create Date: 2026-11-12

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '009'
down_revision: str | None = '008'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create locked_longlist table
    op.create_table(
        'locked_longlist',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('source_proposal_id', sa.Integer(), nullable=False),
        sa.Column('lock_status', sa.String(length=50), nullable=False),
        sa.Column('locked_by', sa.String(length=50), nullable=False),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
        sa.ForeignKeyConstraint(['source_proposal_id'], ['longlist_proposal.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('case_id')
    )
    op.create_index(op.f('ix_locked_longlist_case_id'), 'locked_longlist', ['case_id'], unique=True)
    op.create_index(op.f('ix_locked_longlist_lock_status'), 'locked_longlist', ['lock_status'], unique=False)
    
    # Create locked_supplier table
    op.create_table(
        'locked_supplier',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('locked_longlist_id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('final_rank_position', sa.Integer(), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['locked_longlist_id'], ['locked_longlist.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['supplier.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locked_supplier_locked_longlist_id'), 'locked_supplier', ['locked_longlist_id'], unique=False)
    op.create_index(op.f('ix_locked_supplier_supplier_id'), 'locked_supplier', ['supplier_id'], unique=False)
    
    # Create tender_dispatch table
    op.create_table(
        'tender_dispatch',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('locked_longlist_id', sa.Integer(), nullable=False),
        sa.Column('dispatch_batch_ref', sa.String(length=100), nullable=False),
        sa.Column('dispatch_status', sa.String(length=50), nullable=False),
        sa.Column('dispatched_by', sa.String(length=50), nullable=False),
        sa.Column('dispatched_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['locked_longlist_id'], ['locked_longlist.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('locked_longlist_id'),
        sa.UniqueConstraint('dispatch_batch_ref')
    )
    op.create_index(op.f('ix_tender_dispatch_dispatch_status'), 'tender_dispatch', ['dispatch_status'], unique=False)
    
    # Create tender_dispatch_recipient table
    op.create_table(
        'tender_dispatch_recipient',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('dispatch_id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('delivery_status', sa.String(length=50), nullable=False),
        sa.Column('external_delivery_ref', sa.String(length=200), nullable=True),
        sa.Column('last_attempt_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['dispatch_id'], ['tender_dispatch.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['supplier.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tender_dispatch_recipient_dispatch_id'), 'tender_dispatch_recipient', ['dispatch_id'], unique=False)
    op.create_index(op.f('ix_tender_dispatch_recipient_delivery_status'), 'tender_dispatch_recipient', ['delivery_status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tender_dispatch_recipient_delivery_status'), table_name='tender_dispatch_recipient')
    op.drop_index(op.f('ix_tender_dispatch_recipient_dispatch_id'), table_name='tender_dispatch_recipient')
    op.drop_table('tender_dispatch_recipient')
    
    op.drop_index(op.f('ix_tender_dispatch_dispatch_status'), table_name='tender_dispatch')
    op.drop_table('tender_dispatch')
    
    op.drop_index(op.f('ix_locked_supplier_supplier_id'), table_name='locked_supplier')
    op.drop_index(op.f('ix_locked_supplier_locked_longlist_id'), table_name='locked_supplier')
    op.drop_table('locked_supplier')
    
    op.drop_index(op.f('ix_locked_longlist_lock_status'), table_name='locked_longlist')
    op.drop_index(op.f('ix_locked_longlist_case_id'), table_name='locked_longlist')
    op.drop_table('locked_longlist')
