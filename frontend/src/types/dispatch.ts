export interface TenderDispatch {
  dispatch_id: string;
  longlist_id: string;
  dispatch_batch_id: string;
  supplier_id: string;
  supplier_contact: string | null;
  dispatch_status: 'pending' | 'delivered' | 'retrying' | 'failed' | 'escalated';
  retry_count: number;
  delivery_confirmation_ref: string | null;
  error_detail: string | null;
  escalation_opened: boolean;
  last_attempt_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TenderDispatchRequest {
  longlist_id: string;
  tender_template: string;
  supplier_contacts: SupplierContact[];
}

export interface SupplierContact {
  supplier_id: string;
  contact_email: string;
  contact_name: string;
}

export interface TenderDispatchResponse {
  dispatch_batch_id: string;
  longlist_id: string;
  supplier_dispatches: TenderDispatch[];
  correlation_id: string;
}

export interface LockedSupplier {
  rank: number;
  supplier_id: string;
  supplier_name: string;
  origin: string;
  membership: string;
}
