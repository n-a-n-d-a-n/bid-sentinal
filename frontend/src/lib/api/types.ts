export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'ADMIN' | 'PROCUREMENT_OFFICER' | 'ANALYST' | 'VIEWER';
}

export interface Tender {
  id: string;
  tender_number: string;
  title: string;
  description: string;
  category: string;
  estimated_value: number;
  status: string;
  created_at: string;
}

export interface Requirement {
  id: string;
  requirement_type: string;
  operator: string;
  target_value: string;
  unit?: string;
  is_mandatory: boolean;
}

export interface Bidder {
  id: string;
  canonical_name: string;
  pan?: string;
  gstin?: string;
  cin?: string;
  udyam_number?: string;
  registered_address?: string;
}

export interface Bid {
  id: string;
  tender_id: string;
  bidder_id: string;
  bid_number: string;
  proposed_price: number;
  status: string;
  created_at: string;
}

export interface Document {
  id: string;
  filename: string;
  document_type: string;
  page_count: number;
  ocr_required: boolean;
  file_hash: string;
  created_at: string;
}

export interface VerificationResult {
  provider: string;
  queried_identifier: string;
  returned_identifier?: string;
  status: 'VERIFIED' | 'MISMATCH' | 'UNAVAILABLE' | 'NOT_FOUND' | 'RATE_LIMITED';
  confidence: number;
  is_mock: boolean;
  data?: Record<string, any>;
}

export interface ComplianceSummary {
  status: 'READY_FOR_REVIEW' | 'MANUAL_REVIEW_REQUIRED' | 'BLOCKED' | 'INCOMPLETE';
  passed: number;
  failed: number;
  missing: number;
  total: number;
  items: Array<{
    requirement_name: string;
    status: string;
    extracted_value?: string;
    required_value?: string;
    explanation?: string;
  }>;
}

export interface RiskAnalysis {
  overall_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  components: Record<string, number>;
  factors: Array<{
    factor_name: string;
    weight: number;
    contribution: number;
    explanation: string;
  }>;
}

export interface AnomalyAnalysis {
  anomaly_score: number;
  title: string;
  explanation_summary: string;
  contributing_signals: string[];
  is_anomalous: boolean;
}

export interface GraphNode {
  data: {
    id: string;
    label: string;
    type: string;
  };
}

export interface GraphEdge {
  data: {
    source: string;
    target: string;
    relationship: string;
  };
}

export interface CytoscapeGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface PolicyCitation {
  source: string;
  version: string;
  section: string;
  page: number;
  chunk_id: string;
  relevance: number;
}

export interface PolicyQueryResponse {
  answer: string;
  grounding: 'GROUNDED' | 'PARTIALLY_GROUNDED' | 'INSUFFICIENT_EVIDENCE';
  confidence: string;
  citations: PolicyCitation[];
  limitations: string[];
}

export interface OfficerDecisionRecord {
  id: string;
  bid_id: string;
  officer_id: string;
  decision: string;
  reason: string;
  override_justification?: string;
  decided_at: string;
}

export interface AuditEvent {
  event_id: string;
  action: string;
  user_email: string;
  timestamp: string;
  summary: string;
  details?: Record<string, any>;
  hash?: string;
}

export interface AuditVerification {
  status: 'VALID' | 'INVALID';
  total_events: number;
  verified_events: number;
  broken_event_id?: string;
  message: string;
}

export interface DemoScenario {
  code: string;
  name: string;
  description: string;
  category: string;
  expected_outcome: string;
  tags: string[];
  display_order: number;
}

export interface DemoRunResult {
  demo_run_id: string;
  scenario_code: string;
  scenario_name: string;
  status: string;
  started_at: string;
  completed_at?: string;
  duration_ms: number;
  expected_outcome: string;
  actual_outcome: string;
  outcome_match: boolean;
  stage_results: Record<string, any>;
}
