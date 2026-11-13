export interface ClassificationReview {
  id: string;
  need_id: string;
  classification_verdict: 'single_resource' | 'it_service';
  classification_confidence: number;
  rationale: string;
  review_decision: 'approve' | 'modify' | 'reject';
  reviewer_id: string;
  escalation_required: boolean;
  exemplars_referenced: string[];
  created_at: string;
  updated_at: string;
}

export interface ClassificationReviewRequest {
  review_decision: 'approve' | 'modify' | 'reject';
  classification_verdict: 'single_resource' | 'it_service';
  classification_confidence: number;
  rationale: string;
  exemplars_referenced: string[];
  escalation_required: boolean;
}

export interface ClassificationReviewResponse {
  classification_review_id: string;
  need_id: string;
  review_decision: string;
  classification_verdict: string;
  classification_confidence: number;
  rationale: string;
  exemplars_referenced: string[];
  escalation_required: boolean;
  next_workflow_status: string;
  reviewed_by: string;
  reviewed_at: string;
}

export interface Exemplar {
  id: string;
  verdict: 'single_resource' | 'it_service';
  similarity: number;
  description: string;
}

export interface VmsHandoff {
  id: string;
  need_id: string;
  handover_confirmation: boolean;
  vms_reference_id: string | null;
  workflow_status: string;
  request_payload_json?: string;
  response_payload_json?: string;
  error_detail?: string | null;
  created_at: string;
  updated_at: string;
}

export interface VmsHandoffResponse {
  vms_handoff_id: string;
  need_id: string;
  handover_confirmation: boolean;
  vms_reference_id: string;
  response_payload_json: Record<string, unknown>;
  sent_at: string;
  correlation_id: string;
  workflow_status: string;
}
