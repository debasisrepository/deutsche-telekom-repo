// Case types for Deutsche Telekom IT Procurement

export interface NormalizedNeed {
  id: number
  mandatory_fields: {
    need_title?: string
    business_unit?: string
    need_description?: string
    [key: string]: unknown
  }
  sourced_fields: {
    source_artifact_ref?: string
    source_channel_metadata?: Record<string, unknown>
    [key: string]: unknown
  }
  derived_fields: Record<string, unknown>
  completeness_score: number
}

export interface SourceArtifact {
  id: number
  artifact_type: string
  storage_ref: string
  source_channel: string
  submitted_at: string
}

export interface CaseListItem {
  id: number
  case_number: string
  inbound_channel: string
  workflow_state: string
  next_action: string
  final_classification: string | null
  created_at: string
}

export interface CaseDetail {
  id: number
  case_number: string
  inbound_channel: string
  workflow_state: string
  next_action: string
  final_classification: string | null
  created_by: number
  created_at: string
  updated_at: string
  normalized_need: NormalizedNeed | null
  source_artifacts: SourceArtifact[]
  vms_handoff: unknown | null
}

export interface CreateCaseRequest {
  channel: string
  title: string
  business_unit: string
  description: string
  artifact_type: string
  artifact_ref: string
  submitted_via: string
}

export interface CaseListResponse {
  items: CaseListItem[]
  total: number
  page: number
  page_size: number
}
