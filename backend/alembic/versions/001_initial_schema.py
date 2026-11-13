"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-11-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create needs table
    op.create_table(
        'needs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('business_unit_id', sa.String(length=100), nullable=False),
        sa.Column('channel_type', sa.String(length=50), nullable=False),
        sa.Column('arrival_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('raw_artifact_ref', sa.Text(), nullable=True),
        sa.Column('normalized_payload_json', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=100), nullable=False),
        sa.Column('correlation_id', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('needs') as batch_op:
        batch_op.create_index(batch_op.f('ix_needs_business_unit_id'), ['business_unit_id'])
        batch_op.create_index(batch_op.f('ix_needs_channel_type'), ['channel_type'])
        batch_op.create_index(batch_op.f('ix_needs_arrival_timestamp'), ['arrival_timestamp'])
        batch_op.create_index(batch_op.f('ix_needs_status'), ['status'])
        batch_op.create_index(batch_op.f('ix_needs_correlation_id'), ['correlation_id'])

    # Create need_attributes table
    op.create_table(
        'need_attributes',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('need_id', sa.Uuid(), nullable=False),
        sa.Column('service_type', sa.String(length=200), nullable=True),
        sa.Column('scope_description', sa.Text(), nullable=True),
        sa.Column('estimated_volume_duration', sa.String(length=500), nullable=True),
        sa.Column('required_skills', sa.Text(), nullable=True),
        sa.Column('budget_indication', sa.String(length=200), nullable=True),
        sa.Column('delivery_location', sa.String(length=500), nullable=True),
        sa.Column('field_confidence', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('need_attributes') as batch_op:
        batch_op.create_index(batch_op.f('ix_need_attributes_need_id'), ['need_id'])
        batch_op.create_foreign_key('fk_need_attributes_need_id', 'needs', ['need_id'], ['id'])

    # Create classification_reviews table
    op.create_table(
        'classification_reviews',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('need_id', sa.Uuid(), nullable=False),
        sa.Column('classification_verdict', sa.String(length=50), nullable=False),
        sa.Column('classification_confidence', sa.Float(), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('review_decision', sa.String(length=50), nullable=True),
        sa.Column('reviewer_id', sa.String(length=100), nullable=True),
        sa.Column('escalation_required', sa.Boolean(), nullable=False),
        sa.Column('exemplars_referenced', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('classification_reviews') as batch_op:
        batch_op.create_index(batch_op.f('ix_classification_reviews_need_id'), ['need_id'])
        batch_op.create_index(batch_op.f('ix_classification_reviews_reviewer_id'), ['reviewer_id'])
        batch_op.create_foreign_key('fk_classification_reviews_need_id', 'needs', ['need_id'], ['id'])

    # Create vms_handoffs table
    op.create_table(
        'vms_handoffs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('need_id', sa.Uuid(), nullable=False),
        sa.Column('handover_confirmation', sa.Boolean(), nullable=False),
        sa.Column('vms_reference_id', sa.String(length=200), nullable=True),
        sa.Column('workflow_status', sa.String(length=100), nullable=False),
        sa.Column('request_payload_json', sa.Text(), nullable=True),
        sa.Column('response_payload_json', sa.Text(), nullable=True),
        sa.Column('error_detail', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('vms_handoffs') as batch_op:
        batch_op.create_index(batch_op.f('ix_vms_handoffs_need_id'), ['need_id'])
        batch_op.create_foreign_key('fk_vms_handoffs_need_id', 'needs', ['need_id'], ['id'])

    # Create supplier_evidence_items table
    op.create_table(
        'supplier_evidence_items',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('need_id', sa.Uuid(), nullable=False),
        sa.Column('supplier_id', sa.String(length=100), nullable=False),
        sa.Column('evidence_type', sa.String(length=100), nullable=False),
        sa.Column('source_reference', sa.String(length=500), nullable=False),
        sa.Column('citation_text', sa.Text(), nullable=False),
        sa.Column('quality_rating', sa.Float(), nullable=True),
        sa.Column('evidence_limited_flag', sa.Boolean(), nullable=False),
        sa.Column('evidence_snapshot_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_seed_data', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('supplier_evidence_items') as batch_op:
        batch_op.create_index(batch_op.f('ix_supplier_evidence_items_need_id'), ['need_id'])
        batch_op.create_index(batch_op.f('ix_supplier_evidence_items_supplier_id'), ['supplier_id'])
        batch_op.create_foreign_key('fk_supplier_evidence_items_need_id', 'needs', ['need_id'], ['id'])

    # Create panel_matches table
    op.create_table(
        'panel_matches',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('need_id', sa.Uuid(), nullable=False),
        sa.Column('supplier_id', sa.String(length=100), nullable=False),
        sa.Column('panel_source', sa.String(length=200), nullable=False),
        sa.Column('functional_group', sa.String(length=200), nullable=True),
        sa.Column('provenance_ref', sa.String(length=500), nullable=False),
        sa.Column('coverage_gap_flag', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('panel_matches') as batch_op:
        batch_op.create_index(batch_op.f('ix_panel_matches_need_id'), ['need_id'])
        batch_op.create_index(batch_op.f('ix_panel_matches_supplier_id'), ['supplier_id'])
        batch_op.create_foreign_key('fk_panel_matches_need_id', 'needs', ['need_id'], ['id'])

    # Create provider_candidates table
    op.create_table(
        'provider_candidates',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('need_id', sa.Uuid(), nullable=False),
        sa.Column('candidate_name', sa.String(length=200), nullable=False),
        sa.Column('supplier_id', sa.String(length=100), nullable=True),
        sa.Column('capability_gap', sa.Text(), nullable=False),
        sa.Column('source_citations', sa.Text(), nullable=False),
        sa.Column('review_status', sa.String(length=50), nullable=False),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('provider_candidates') as batch_op:
        batch_op.create_index(batch_op.f('ix_provider_candidates_need_id'), ['need_id'])
        batch_op.create_index(batch_op.f('ix_provider_candidates_supplier_id'), ['supplier_id'])
        batch_op.create_foreign_key('fk_provider_candidates_need_id', 'needs', ['need_id'], ['id'])

    # Create longlist_proposals table
    op.create_table(
        'longlist_proposals',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('need_id', sa.Uuid(), nullable=False),
        sa.Column('ranked_suppliers', sa.Text(), nullable=False),
        sa.Column('evidence_limited_flag', sa.Boolean(), nullable=False),
        sa.Column('review_status', sa.String(length=50), nullable=False),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('longlist_proposals') as batch_op:
        batch_op.create_index(batch_op.f('ix_longlist_proposals_need_id'), ['need_id'])
        batch_op.create_foreign_key('fk_longlist_proposals_need_id', 'needs', ['need_id'], ['id'])

    # Create longlist_ranked_suppliers table
    op.create_table(
        'longlist_ranked_suppliers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('proposal_id', sa.Uuid(), nullable=False),
        sa.Column('supplier_id', sa.String(length=100), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('panel_source', sa.String(length=200), nullable=True),
        sa.Column('evidence_citations', sa.Text(), nullable=False),
        sa.Column('rank_rationale', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('longlist_ranked_suppliers') as batch_op:
        batch_op.create_index(batch_op.f('ix_longlist_ranked_suppliers_proposal_id'), ['proposal_id'])
        batch_op.create_index(batch_op.f('ix_longlist_ranked_suppliers_supplier_id'), ['supplier_id'])
        batch_op.create_foreign_key('fk_longlist_ranked_suppliers_proposal_id', 'longlist_proposals', ['proposal_id'], ['id'])

    # Create supplier_count_validations table
    op.create_table(
        'supplier_count_validations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('proposal_id', sa.Uuid(), nullable=False),
        sa.Column('supplier_count', sa.Integer(), nullable=False),
        sa.Column('validation_verdict', sa.String(length=50), nullable=False),
        sa.Column('violations', sa.Text(), nullable=True),
        sa.Column('triggered_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('supplier_count_validations') as batch_op:
        batch_op.create_index(batch_op.f('ix_supplier_count_validations_proposal_id'), ['proposal_id'])
        batch_op.create_foreign_key('fk_supplier_count_validations_proposal_id', 'longlist_proposals', ['proposal_id'], ['id'])

    # Create longlists table
    op.create_table(
        'longlists',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('need_id', sa.Uuid(), nullable=False),
        sa.Column('proposal_id', sa.Uuid(), nullable=True),
        sa.Column('suppliers', sa.Text(), nullable=False),
        sa.Column('locked', sa.Boolean(), nullable=False),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('locked_by', sa.String(length=100), nullable=True),
        sa.Column('validation_verdict_at_lock', sa.String(length=50), nullable=True),
        sa.Column('change_history', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('longlists') as batch_op:
        batch_op.create_index(batch_op.f('ix_longlists_need_id'), ['need_id'])
        batch_op.create_index(batch_op.f('ix_longlists_proposal_id'), ['proposal_id'])
        batch_op.create_foreign_key('fk_longlists_need_id', 'needs', ['need_id'], ['id'])
        batch_op.create_foreign_key('fk_longlists_proposal_id', 'longlist_proposals', ['proposal_id'], ['id'])

    # Create longlist_adjustments table
    op.create_table(
        'longlist_adjustments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('longlist_id', sa.Uuid(), nullable=False),
        sa.Column('supplier_id', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('actor', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('longlist_adjustments') as batch_op:
        batch_op.create_index(batch_op.f('ix_longlist_adjustments_longlist_id'), ['longlist_id'])
        batch_op.create_index(batch_op.f('ix_longlist_adjustments_supplier_id'), ['supplier_id'])
        batch_op.create_foreign_key('fk_longlist_adjustments_longlist_id', 'longlists', ['longlist_id'], ['id'])

    # Create tender_dispatches table
    op.create_table(
        'tender_dispatches',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('longlist_id', sa.Uuid(), nullable=False),
        sa.Column('dispatch_batch_id', sa.String(length=100), nullable=False),
        sa.Column('supplier_id', sa.String(length=100), nullable=False),
        sa.Column('supplier_contact', sa.String(length=500), nullable=True),
        sa.Column('dispatch_status', sa.String(length=50), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('delivery_confirmation_ref', sa.String(length=200), nullable=True),
        sa.Column('error_detail', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('tender_dispatches') as batch_op:
        batch_op.create_index(batch_op.f('ix_tender_dispatches_longlist_id'), ['longlist_id'])
        batch_op.create_index(batch_op.f('ix_tender_dispatches_dispatch_batch_id'), ['dispatch_batch_id'])
        batch_op.create_index(batch_op.f('ix_tender_dispatches_supplier_id'), ['supplier_id'])
        batch_op.create_foreign_key('fk_tender_dispatches_longlist_id', 'longlists', ['longlist_id'], ['id'])

    # Create audit_events table
    op.create_table(
        'audit_events',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('need_id', sa.Uuid(), nullable=True),
        sa.Column('correlation_id', sa.String(length=100), nullable=False),
        sa.Column('step_code', sa.String(length=50), nullable=False),
        sa.Column('agent_code', sa.String(length=50), nullable=True),
        sa.Column('tool_code', sa.String(length=50), nullable=True),
        sa.Column('actor_type', sa.String(length=50), nullable=False),
        sa.Column('actor_id', sa.String(length=100), nullable=True),
        sa.Column('outcome', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('payload_ref', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('audit_events') as batch_op:
        batch_op.create_index(batch_op.f('ix_audit_events_need_id'), ['need_id'])
        batch_op.create_index(batch_op.f('ix_audit_events_correlation_id'), ['correlation_id'])
        batch_op.create_index(batch_op.f('ix_audit_events_step_code'), ['step_code'])
        batch_op.create_index(batch_op.f('ix_audit_events_actor_id'), ['actor_id'])
        batch_op.create_index(batch_op.f('ix_audit_events_created_at'), ['created_at'])


def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('tender_dispatches')
    op.drop_table('longlist_adjustments')
    op.drop_table('longlists')
    op.drop_table('supplier_count_validations')
    op.drop_table('longlist_ranked_suppliers')
    op.drop_table('longlist_proposals')
    op.drop_table('provider_candidates')
    op.drop_table('panel_matches')
    op.drop_table('supplier_evidence_items')
    op.drop_table('vms_handoffs')
    op.drop_table('classification_reviews')
    op.drop_table('need_attributes')
    op.drop_table('needs')
