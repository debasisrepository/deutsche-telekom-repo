export interface EvidenceItem {
  supplier_id: string;
  evidence_type: string;
  source_system: string;
  source_reference: string;
  service_category: string;
  business_unit: string | null;
  delivery_period: string | null;
  quality_rating: number | null;
  citation_text: string;
  is_seed_data: boolean;
  snapshot_timestamp: string;
}

export interface EvidenceQueryResponse {
  evidence_items: EvidenceItem[];
  evidence_limited_flag: boolean;
  evidence_snapshot_timestamp: string;
  correlation_id: string | null;
}

export interface CandidateSupplier {
  panel_match_id: string;
  supplier_id: string;
  panel_source: string;
  functional_group: string;
  provenance_ref: string;
}

export interface PanelMappingResponse {
  need_id: string;
  candidate_suppliers: CandidateSupplier[];
  coverage_gap_flag: boolean;
  correlation_id: string;
}
