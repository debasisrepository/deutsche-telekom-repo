export interface NeedAttribute {
  field: string;
  value: string;
  confidence: number;
  action?: 'keep' | 'modify';
}

export interface NeedAttributesData {
  id: string;
  need_id: string;
  service_type?: string;
  scope_description?: string;
  estimated_volume_duration?: string;
  required_skills?: string | string[];
  budget_indication?: string;
  delivery_location?: string;
  field_confidence?: string | Record<string, number>;
  schema_valid?: boolean;
  review_status?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface AttributeReviewRequest {
  review_decision: 'approve' | 'modify' | 'reject';
  need_attributes?: {
    service_type?: string;
    scope_description?: string;
    estimated_volume_duration?: string;
    required_skills?: string;
    budget_indication?: string;
    delivery_location?: string;
    field_confidence?: string;
  };
  reviewer_notes?: string;
}

export interface AttributeReviewResponse {
  need_id: string;
  review_decision: string;
  next_workflow_status: string;
  need_attributes_id: string;
}
