export interface Need {
  id: string;
  business_unit_id: string;
  channel_type: 'rfp' | 'email' | 'phone' | 'supplier_offer';
  arrival_timestamp: string;
  raw_artifact_ref?: string;
  normalized_payload_json?: string;
  status: string;
  classification_verdict?: string;
  classification_confidence?: number;
  evidence_limited_flag: boolean;
  correlation_id: string;
  created_at: string;
  updated_at: string;
}

export interface NeedDetailResponse extends Need {
  pii_masked?: boolean;
  masked_count?: number;
}

export interface ChannelHealth {
  channel: string;
  today: number;
  rejected: number;
}

export interface NeedIntakeStats {
  received_today: number;
  normalized: number;
  rejected: number;
  normalized_within_threshold_percent: number;
}
