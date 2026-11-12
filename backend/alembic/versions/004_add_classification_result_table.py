"""add classification_result table

Revision ID: 004
Revises: 003
Create Date: 2026-11-12 14:30:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'classification_result',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('ai_verdict', sa.String(length=50), nullable=False),
        sa.Column('confirmed_verdict', sa.String(length=50), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('rationale_inputs', sa.Text(), nullable=False),
        sa.Column('overridden', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('requirement_tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['need_case.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('case_id')
    )
    
    with op.batch_alter_table('classification_result', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_classification_result_case_id'), ['case_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_classification_result_created_at'), ['created_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('classification_result', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_classification_result_created_at'))
        batch_op.drop_index(batch_op.f('ix_classification_result_case_id'))
    
    op.drop_table('classification_result')
