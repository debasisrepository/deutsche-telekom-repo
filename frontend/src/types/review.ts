// Review types for Deutsche Telekom IT Procurement

export interface ExtractedAttribute {
  value: string | string[]
  source_excerpt?: string
  confidence?: number
  lineage: 'ai_generated' | 'human_corrected' | 'directly_sourced'
}

export interface ExtractionReviewPayload {
  [attributeName: string]: ExtractedAttribute
}

export interface ClassificationRationaleInput {
  [key: string]: unknown
}

export interface ClassificationReviewPayload {
  ai_verdict: 'it_service' | 'single_resource'
  confidence_score: number
  rationale_inputs: ClassificationRationaleInput
  reasoning?: string
}

export interface ExtractionReviewDecisionRequest {
  decision: 'approve' | 'edit' | 'reject'
  edited_attributes?: ExtractionReviewPayload
}

export interface ClassificationReviewDecisionRequest {
  decision: 'confirm' | 'override'
  confirmed_verdict?: 'it_service' | 'single_resource'
}

export interface ReviewDecisionResponse {
  review_id: number
  case_id: number
  review_type: string
  status: string
  decision: string
  reviewer_id: number
  reviewed_at: string
  next_workflow_state: string
  next_action: string
}
