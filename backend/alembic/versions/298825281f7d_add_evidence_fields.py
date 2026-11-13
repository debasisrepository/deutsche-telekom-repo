"""add_evidence_fields

Revision ID: 298825281f7d
Revises: b85316146bea
Create Date: 2026-11-13 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '298825281f7d'
down_revision: Union[str, None] = 'b85316146bea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to supplier_evidence_items
    with op.batch_alter_table('supplier_evidence_items') as batch_op:
        batch_op.add_column(sa.Column('source_system', sa.String(64), nullable=False, server_default='SEED'))
        batch_op.add_column(sa.Column('service_category', sa.String(128), nullable=False, server_default='general'))
        batch_op.add_column(sa.Column('business_unit_id', sa.String(64), nullable=True))
        batch_op.add_column(sa.Column('delivery_period', sa.String(128), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('supplier_evidence_items') as batch_op:
        batch_op.drop_column('delivery_period')
        batch_op.drop_column('business_unit_id')
        batch_op.drop_column('service_category')
        batch_op.drop_column('source_system')
