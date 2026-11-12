"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-11-12

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    
    # Create need_case table
    op.create_table(
        'need_case',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_number', sa.String(length=50), nullable=False),
        sa.Column('inbound_channel', sa.String(length=50), nullable=False),
        sa.Column('workflow_state', sa.String(length=50), nullable=False),
        sa.Column('next_action', sa.String(length=100), nullable=False),
        sa.Column('final_classification', sa.String(length=50), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_need_case_case_number'), 'need_case', ['case_number'], unique=True)
    op.create_index(op.f('ix_need_case_inbound_channel'), 'need_case', ['inbound_channel'], unique=False)
    op.create_index(op.f('ix_need_case_workflow_state'), 'need_case', ['workflow_state'], unique=False)
    op.create_index(op.f('ix_need_case_final_classification'), 'need_case', ['final_classification'], unique=False)
    op.create_index(op.f('ix_need_case_created_by'), 'need_case', ['created_by'], unique=False)
    op.create_index(op.f('ix_need_case_created_at'), 'need_case', ['created_at'], unique=False)
    
    # Create normalized_need table
    op.create_table(
        'normalized_need',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('mandatory_fields', sa.Text(), nullable=False),
        sa.Column('sourced_fields', sa.Text(), nullable=False),
        sa.Column('derived_fields', sa.Text(), nullable=False),
        sa.Column('completeness_score', sa.Float(), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_normalized_need_case_id'), 'normalized_need', ['case_id'], unique=True)
    
    # Create source_artifact table
    op.create_table(
        'source_artifact',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('artifact_type', sa.String(length=50), nullable=False),
        sa.Column('storage_ref', sa.String(length=500), nullable=False),
        sa.Column('source_channel', sa.String(length=50), nullable=False),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_source_artifact_case_id'), 'source_artifact', ['case_id'], unique=False)
    op.create_index(op.f('ix_source_artifact_submitted_at'), 'source_artifact', ['submitted_at'], unique=False)
    
    # Create workflow_event table
    op.create_table(
        'workflow_event',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('from_state', sa.String(length=50), nullable=True),
        sa.Column('to_state', sa.String(length=50), nullable=False),
        sa.Column('actor_type', sa.String(length=50), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('payload', sa.Text(), nullable=True),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_event_case_id'), 'workflow_event', ['case_id'], unique=False)
    op.create_index(op.f('ix_workflow_event_event_type'), 'workflow_event', ['event_type'], unique=False)
    op.create_index(op.f('ix_workflow_event_actor_id'), 'workflow_event', ['actor_id'], unique=False)
    op.create_index(op.f('ix_workflow_event_created_at'), 'workflow_event', ['created_at'], unique=False)
    
    # Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('actor_type', sa.String(length=50), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('target_type', sa.String(length=50), nullable=True),
        sa.Column('target_id', sa.String(length=50), nullable=True),
        sa.Column('audit_payload', sa.Text(), nullable=True),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_log_case_id'), 'audit_log', ['case_id'], unique=False)
    op.create_index(op.f('ix_audit_log_action_type'), 'audit_log', ['action_type'], unique=False)
    op.create_index(op.f('ix_audit_log_actor_id'), 'audit_log', ['actor_id'], unique=False)
    op.create_index(op.f('ix_audit_log_created_at'), 'audit_log', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('audit_log')
    op.drop_table('workflow_event')
    op.drop_table('source_artifact')
    op.drop_table('normalized_need')
    op.drop_table('need_case')
    op.drop_table('user')
