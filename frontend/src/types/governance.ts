export interface SupplierCountValidation {
  validation_id: string;
  proposal_id: string;
  supplier_count: number;
  validation_verdict: 'pass' | 'fail';
  violations: string[];
  triggered_by: string;
  created_at: string;
}

export interface LonglistAdjustment {
  adjustment_id: string;
  longlist_id: string;
  supplier_id: string;
  action: 'add' | 'remove';
  reason: string;
  actor: string;
  timestamp: string;
}

export interface LonglistAdjustmentRequest {
  supplier_id: string;
  action: 'add' | 'remove';
  reason: string;
  actor: string;
  timestamp?: string;
}

export interface LonglistAdjustmentResponse {
  adjustment_id: string;
  longlist_id: string;
  updated_suppliers: string[];
  validation_verdict: 'pass' | 'fail';
  change_history_count: number;
  correlation_id: string;
}

export interface Longlist {
  longlist_id: string;
  need_id: string;
  proposal_id: string;
  suppliers: string[];
  locked: boolean;
  locked_at: string | null;
  locked_by: string | null;
  validation_verdict_at_lock: string | null;
  change_history: ChangeHistoryEntry[];
  created_at: string;
  updated_at: string;
}

export interface ChangeHistoryEntry {
  action: string;
  timestamp: string;
  actor: string;
  supplier_ids?: string[];
  validation_verdict?: string;
  supplier_id?: string;
  reason?: string;
}

export interface LonglistLockRequest {
  expected_validation_verdict: 'pass';
  supplier_ids: string[];
  finalized_by: string;
}

export interface LonglistLockResponse {
  longlist_id: string;
  need_id: string;
  suppliers: string[];
  locked: boolean;
  locked_at: string;
  change_history: ChangeHistoryEntry[];
  validation_count: number;
  correlation_id: string;
}

export interface RankedSupplier {
  supplier_id: string;
  rank: number;
  panel_source: string;
  status?: 'On list' | 'Removed by BU';
  removal_adjustment_number?: number;
}
