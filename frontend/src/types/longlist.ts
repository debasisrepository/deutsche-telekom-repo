export interface EvidenceCitation {
  citation_label: string
  citation_ref: string
  evidence_summary?: string
}

export interface RankedSupplier {
  supplier_id: number
  supplier_code: string
  supplier_name: string
  rank_position: number
  ranking_score: number
  recommendation_status: string
  citation_complete: boolean
  evidence_citations: EvidenceCitation[]
  origin?: 'ai_generated' | 'human_added'
}

export interface LonglistProposal {
  items: RankedSupplier[]
  total: number
  proposal_id: number
  version_no: number
  proposal_status: string
  created_at: string
}

export interface SupplierAdjustment {
  adjustment_id: number
  case_id: number
  supplier_id: number
  change_type: 'add' | 'remove'
  rationale: string
  actor_id: string
  resulting_supplier_count: number
  created_at: string
}

export interface ValidationResult {
  validation_id: number
  case_id: number
  validation_type: string
  supplier_count: number
  validation_result: 'valid' | 'invalid_low' | 'invalid_high'
  rule_snapshot: string
  validation_message: string
  validated_at: string
}

export interface LockedSupplier {
  locked_supplier_id: number
  supplier_id: number
  final_rank_position: number
}

export interface LockedLonglist {
  locked_longlist_id: number
  case_id: number
  source_proposal_id: number
  lock_status: string
  locked_by: string
  locked_at: string
  locked_suppliers: LockedSupplier[]
  total_suppliers: number
}

export interface DispatchRecipient {
  recipient_id: number
  supplier_id: number
  delivery_status: 'success' | 'failed'
  external_delivery_ref: string | null
  last_attempt_at?: string
}

export interface TenderDispatch {
  dispatch_id: number
  dispatch_batch_ref: string
  dispatch_status: 'success' | 'partial_failure' | 'failed'
  dispatched_by: string
  dispatched_at: string
  recipients: DispatchRecipient[]
  total_recipients: number
}
