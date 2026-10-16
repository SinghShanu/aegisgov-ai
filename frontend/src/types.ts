export interface UserPersona {
  user_id: string;
  name: string;
  role: 'JUNIOR_ANALYST' | 'WEALTH_ADVISOR' | 'COMPLIANCE_OFFICER' | 'RISK_OFFICER' | 'DATA_ENGINEER';
  clearance: 'INTERNAL' | 'CONFIDENTIAL' | 'RESTRICTED' | 'SECRET';
  jurisdiction: 'SG' | 'IN' | 'JP' | 'GLOBAL';
  allowed_actions: string[];
  max_transaction_limit_sgd: number;
  max_transaction_limit_inr: number;
  can_approve_hitl: boolean;
  session_token: string;
  token_ttl_seconds: number;
}

export interface ColumnContractRule {
  column_name: string;
  data_type: string;
  nullable: boolean;
  pii_type: string;
  masking_strategy: string;
  description: string;
}

export interface DataContract {
  contract_id: string;
  name: string;
  version: string;
  target_tier: string;
  jurisdiction: string;
  governing_regulation: string;
  rules: ColumnContractRule[];
  created_at: number;
  status: 'PENDING_APPROVAL' | 'ACTIVE_ENFORCING' | 'DEPRECATED';
  approved_by?: string;
  approved_at?: string;
  is_active: boolean;
  lifecycle_telemetry?: {
    cycle_status: string;
    pipeline_summary: {
      bronze_total: number;
      silver_promoted: number;
      quarantined: number;
    };
    gold_certified_metrics: {
      compliance_health_score: number;
      total_certified_transactions: number;
      total_volume_sgd: number;
      total_volume_inr: number;
    };
    deployed_at: string;
    compliance_remarks?: string;
  };
}

export interface HITLTicket {
  ticket_id: string;
  created_at: number;
  formatted_time: string;
  trigger_type: string;
  requester_id: string;
  requester_name: string;
  requester_role: string;
  requester_jurisdiction: string;
  description: string;
  proposed_action: string;
  amount_sgd: number;
  amount_inr: number;
  payload: Record<string, any>;
  risk_score: number;
  risk_summary: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'QUARANTINED';
  reviewed_by?: string;
  reviewed_at?: number;
  review_remarks?: string;
  audit_entry_id?: string;
}

export interface AuditEntry {
  entry_id: string;
  timestamp: number;
  formatted_time: string;
  event_type: string;
  user_id: string;
  role: string;
  action_or_prompt: string;
  decision: string;
  threat_score: number;
  violating_policies: string[];
  previous_hash: string;
  entry_hash: string;
}

export interface GoldAnalytics {
  total_certified_transactions: number;
  total_volume_sgd: number;
  total_volume_inr: number;
  avg_transaction_sgd: number;
  compliance_health_score: number;
  quarantine_count: number;
  capital_safeguarded_sgd?: number;
  hitl_dual_custody_compliance_rate?: number;
  pdpa_pii_tokenization_rate?: number;
  basel_iii_liquidity_classification?: string;
  payment_rails_breakdown: Array<{ payment_rail: string; count: number; rail_volume_sgd: number }>;
  currency_distribution: Array<{ currency: string; count: number; total_native: number }>;
  certified_status?: string;
  executive_leadership_summary?: {
    executive_question: string;
    certified_answer: string;
    auditor_attestation_seal: string;
    attestation_timestamp: string;
  };
}

export interface GoldMartRecord {
  payment_rail: string;
  currency: string;
  settlement_count: number;
  rail_volume_sgd: number;
  rail_volume_inr: number;
  avg_ticket_sgd: number;
  peak_single_exposure_sgd: number;
  mas_compliance_status: string;
  rbi_compliance_status: string;
  pii_protection_sla: string;
}

export interface SentinelExecutionResponse {
  status: 'COMPLETED' | 'DENIED_ACCESS' | 'BLOCKED_ATTACK' | 'PENDING_HITL_APPROVAL';
  reply: string;
  access_decision: {
    allowed: boolean;
    status: string;
    reason: string;
    violating_policy?: string;
  };
  ingress_inspection: {
    allowed: boolean;
    threat_score: number;
    threat_level: string;
    attack_indicators: string[];
    sanitized_prompt: string;
    detected_pii: Array<{ pii_type: string; masked_token: string }>;
  };
  circuit_breaker?: {
    triggered: boolean;
    requires_hitl: boolean;
    hard_blocked: boolean;
    risk_level: string;
    reason: string;
    amount_sgd: number;
  };
  egress_inspection?: {
    passed: boolean;
    grounding_score: number;
    hallucination_detected: boolean;
    bias_or_policy_violations: string[];
    leaked_secrets_intercepted: string[];
  };
  hitl_ticket_id?: string;
  audit_entry_id?: string;
}

// Backward compatibility alias
export type CopilotResponse = SentinelExecutionResponse;

export interface StreamEvent {
  transaction_id: string;
  timestamp: string;
  payment_rail: string;
  currency: string;
  category: string;
  sender_name: string;
  recipient_name: string;
  amount: number;
  amount_sgd: number;
  status: string;
  description: string;
  ticket_id?: string;
  threat_type?: string;
}

export interface StreamStatus {
  is_running: boolean;
  interval_seconds: number;
  total_generated: number;
  total_promoted_silver: number;
  total_quarantined: number;
  total_hitl_triggered: number;
  rail_counts: Record<string, number>;
  gold_analytics: GoldAnalytics;
  recent_events: StreamEvent[];
}

export interface GCPServiceDetail {
  service_name: string;
  category: string;
  problem_addressed: string;
  gcp_product: string;
  architecture_role: string;
  operational_mode: string;
  status: string;
  icon_name: string;
  regulatory_relevance: string;
}

export interface GCPArchitectureOverview {
  project_id: string;
  region: string;
  gcp_mode: string;
  base_currency: string;
  services: GCPServiceDetail[];
  timestamp: string;
}

export interface RegressionTestCase {
  test_id: string;
  title: string;
  category: string;
  user_persona_key: string;
  prompt: string;
  expected_status: string;
  expected_keywords: string[];
  forbidden_keywords: string[];
  discovered_by: string;
  discovery_notes: string;
  created_at: string;
  is_baseline: boolean;
}

export interface RegressionTestResult {
  test_id: string;
  title: string;
  category: string;
  user_persona_key: string;
  prompt: string;
  passed: boolean;
  expected_status: string;
  actual_status: string;
  expected_keywords_passed: boolean;
  forbidden_keywords_passed: boolean;
  execution_time_ms: number;
  actual_reply_snippet: string;
  diagnostic_hint?: string;
  executed_at: string;
}

export interface RegressionSuiteReport {
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  pass_rate_percentage: number;
  risk_level: string;
  suite_execution_time_ms: number;
  results: RegressionTestResult[];
  summary_notes: string;
  generated_at: string;
}
