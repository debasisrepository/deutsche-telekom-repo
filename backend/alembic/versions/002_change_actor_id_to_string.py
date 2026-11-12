"""change actor_id to string

Revision ID: 002
Revises: 001
Create Date: 2026-11-12 13:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # For workflow_event: change actor_id from Integer to String(50) and drop the FK
    # Use naming_convention to find the auto-generated FK name
    with op.batch_alter_table(
        'workflow_event',
        schema=None,
        naming_convention={"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"}
    ) as batch_op:
        # Drop the FK constraint first (it will be auto-detected by naming convention)
        batch_op.drop_constraint('fk_workflow_event_actor_id_user', type_='foreignkey')
        batch_op.alter_column('actor_id',
                              existing_type=sa.INTEGER(),
                              type_=sa.String(length=50),
                              nullable=False)
    
    # Same for audit_log
    with op.batch_alter_table(
        'audit_log',
        schema=None,
        naming_convention={"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"}
    ) as batch_op:
        batch_op.drop_constraint('fk_audit_log_actor_id_user', type_='foreignkey')
        batch_op.alter_column('actor_id',
                              existing_type=sa.INTEGER(),
                              type_=sa.String(length=50),
                              nullable=False)


def downgrade() -> None:
    # Revert audit_log.actor_id to Integer nullable with FK
    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        batch_op.alter_column('actor_id',
                              existing_type=sa.String(length=50),
                              type_=sa.INTEGER(),
                              nullable=True)
        batch_op.create_foreign_key(None, 'user', ['actor_id'], ['id'])
    
    # Revert workflow_event.actor_id to Integer nullable with FK
    with op.batch_alter_table('workflow_event', schema=None) as batch_op:
        batch_op.alter_column('actor_id',
                              existing_type=sa.String(length=50),
                              type_=sa.INTEGER(),
                              nullable=True)
        batch_op.create_foreign_key(None, 'user', ['actor_id'], ['id'])
