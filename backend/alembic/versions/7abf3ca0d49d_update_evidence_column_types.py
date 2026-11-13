"""update_evidence_column_types

Revision ID: 7abf3ca0d49d
Revises: 298825281f7d
Create Date: 2026-11-13 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7abf3ca0d49d'
down_revision: Union[str, None] = '298825281f7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update column types to match model
    with op.batch_alter_table('supplier_evidence_items') as batch_op:
        batch_op.alter_column('supplier_id', type_=sa.String(128), existing_type=sa.String(100))
        batch_op.alter_column('evidence_type', type_=sa.String(64), existing_type=sa.String(100))
        batch_op.alter_column('source_reference', type_=sa.Text(), existing_type=sa.String(500))


def downgrade() -> None:
    with op.batch_alter_table('supplier_evidence_items') as batch_op:
        batch_op.alter_column('source_reference', type_=sa.String(500), existing_type=sa.Text())
        batch_op.alter_column('evidence_type', type_=sa.String(100), existing_type=sa.String(64))
        batch_op.alter_column('supplier_id', type_=sa.String(100), existing_type=sa.String(128))
