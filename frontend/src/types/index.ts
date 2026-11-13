export interface User {
  email: string;
  role: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ApiError {
  detail: string;
  status_code?: number;
  correlation_id?: string;
}

export interface Need {
  id: string;
  business_unit_id: string;
  channel_type: string;
  arrival_timestamp: string;
  status: string;
  correlation_id: string;
  created_at: string;
  updated_at: string;
}

export interface NeedAttributes {
  id: string;
  need_id: string;
  service_type: string;
  scope_description: string;
  estimated_volume_duration: string;
  required_skills: string[];
  budget_indication: string;
  delivery_location: string;
  created_at: string;
  updated_at: string;
}
