export interface NicheResearchDossierItem {
  provider_candidate_id: string;
  candidate_name: string;
  supplier_id: string;
  capability_gap: string;
  source_citations: string[];
  review_status: string;
  review_notes: string | null;
}

export interface NicheResearchResponse {
  need_id: string;
  niche_research_dossier: NicheResearchDossierItem[];
  review_required: boolean;
  correlation_id: string;
}

export interface EvidenceCitation {
  source_reference: string;
  citation_text: string;
}

export interface RankedSupplier {
  ranked_supplier_id: string;
  supplier_id: string;
  rank: number;
  panel_source: string;
  evidence_citations: EvidenceCitation[];
  rank_rationale: string;
  confidence: number;
}

export interface LonglistProposalResponse {
  proposal_id: string;
  need_id: string;
  ranked_suppliers: RankedSupplier[];
  evidence_limited_flag: boolean;
  proposal_status: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  correlation_id: string | null;
}
