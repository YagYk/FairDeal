export enum CompanyType {
  SERVICE = 'service',
  PRODUCT = 'product',
  STARTUP = 'startup',
}

export enum ExtractionMethod {
  REGEX = 'regex',
  SNIPER_LLM = 'sniper_llm',
  LLM_FALLBACK = 'llm_fallback',
  MISSING = 'missing',
}

export interface ExtractedField {
  value: any;
  confidence: number;
  source_text?: string;
  page_number?: number;
  method: ExtractionMethod;
}

export enum ClauseType {
  TERMINATION = 'termination',
  IP = 'ip',
  NON_COMPETE = 'non_compete',
  CONFIDENTIALITY = 'confidentiality',
  COMPENSATION = 'compensation',
  GENERAL = 'general',
}

export interface ExtractedClause {
  text?: string;
  evidence?: ExtractedField;
}

export interface ContractExtractionResult {
  role?: ExtractedField;
  company_type?: ExtractedField;
  experience_level?: ExtractedField;
  ctc_inr?: ExtractedField;
  notice_period_days?: ExtractedField;
  bond_amount_inr?: ExtractedField;
  non_compete_months?: ExtractedField;
  probation_months?: ExtractedField;
  benefits: string[];
  benefits_count: number;
  extracted_clauses: Record<string, ExtractedClause>;
}

export interface BenchmarkResult {
  percentile_salary?: number;
  percentile_notice?: number;
  cohort_size: number;
  filters_used: Record<string, any>;
  broaden_steps: string[];
  market_mean: number;
  market_median: number;
  market_p25: number;
  market_p75: number;
  warning?: string;
  notice_mean?: number;
  notice_median?: number;
}

export interface EvidenceChunk {
  contract_id: string;
  chunk_id: string;
  clause_type: ClauseType;
  similarity: number;
  text_preview: string;
  metadata: Record<string, any>;
}

export interface ClauseDriftResult {
  clause_type: ClauseType;
  similarity_to_gold: number;
  status: 'standard' | 'anomalous';
  matched_gold_clause_preview: string;
  retrieved_examples: EvidenceChunk[];
}

export interface ScoreBreakdownItem {
  factor: string;
  points: number;
  reason: string;
  source_text?: string;
}

export enum Severity {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export interface RedFlag {
  id: string;
  severity: Severity;
  rule: string;
  explanation: string;
  source_text?: string;
  impact_score: number;
  market_context?: string;
  recommendation: string;
}

export interface FavorableTerm {
  id: string;
  term: string;
  explanation: string;
  source_text?: string;
  value: string;
  impact_score: number;
  market_context?: string;
}

export interface NegotiationPoint {
  id: string;
  priority: number;
  topic: string;
  current_term: string;
  target_term: string;
  rationale: string;
  success_probability: string;
  script: string;
  fallback?: string;
  evidence: string[];
}

export interface PercentileResult {
  value: number;
  interpretation: 'excellent' | 'above_average' | 'average' | 'below_average' | 'poor';
  field_value: any;
  field_display: string;
  cohort_size: number;
  insight: string;
  market_benchmarks?: Record<string, string>;
}

export interface CohortInfo {
  filters_used: Record<string, any>;
  filters_removed: string[];
  cohort_size: number;
  broaden_steps: string[];
  min_n: number;
  confidence_note: string;
}

export interface ScoreResult {
  overall_score: number;
  grade: 'EXCEPTIONAL' | 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR' | 'CRITICAL' | 'BELOW AVERAGE' | 'AVERAGE';
  score_confidence: number;
  score_formula: string;
  breakdown: ScoreBreakdownItem[];
  safety_score: number;
  market_fairness_score: number;
  badges: string[];
  risk_factors: string[];
  legal_violations: string[];
}

export interface ContractMetadata {
  contract_type?: string;
  industry?: string;
  role_level?: string;
  role_title?: string;
  company_name?: string;
  location?: string;
  benefits: string[];
  benefits_count: number;
}

export interface NarrationResult {
  summary: string;
  confidence: number;
  model: string;
  tokens: number;
}

export interface Timings {
  parse_ms: number;
  extract_ms: number;
  benchmark_ms: number;
  rag_ms: number;
  scoring_ms: number;
  narration_ms: number;
  total_ms: number;
}

export interface AnalyzeResponse {
  // Core
  extraction: ContractExtractionResult;
  contract_metadata: ContractMetadata;

  // Scoring
  score: number;
  grade: string;
  scoring: ScoreResult;

  // Percentiles
  percentiles: Record<string, PercentileResult>;
  cohort?: CohortInfo;

  // Intelligence
  red_flags: RedFlag[];
  favorable_terms: FavorableTerm[];
  negotiation_points: NegotiationPoint[];

  // RAG Evidence
  benchmark?: BenchmarkResult;
  rag: RAGResult;
  evidence: EvidenceChunk[];

  // Narration
  narration?: NarrationResult;

  // Meta
  timings: Timings;
  cache: CacheInfo;
  determinism: DeterminismInfo;
}

export interface KBContractMetadata {
  contract_id: string;
  filename: string;
  company_type?: CompanyType;
  role?: string;
  extra: Record<string, any>;
}

export interface KBStats {
  num_contracts: number;
  num_chunks: number;
  clause_type_counts: Record<string, number>;
}

export interface KBChunkPreview {
  contract_id: string;
  chunk_id: string;
  clause_type: ClauseType;
  text_preview: string;
  similarity?: number;
}

export interface KBContractsResponse {
  contracts: KBContractMetadata[];
  total: number;
  offset: number;
  limit: number;
  filters_applied: Record<string, any>;
}

export interface Context {
  role: string;
  experience_level: number;
  company_type: CompanyType;
  location?: string;
  industry?: string;
}

export interface KBHealth {
  chroma_path: string;
  processed_count: number;
  collection_count: number;
}

export interface RAGResult {
  evidence_by_clause_type: Record<string, EvidenceChunk[]>;
  drift_by_clause_type: ClauseDriftResult[];
}

export interface CacheInfo {
  hit: boolean;
  key: string;
}

export interface DeterminismInfo {
  scoring: string;
  extraction: string;
  narration: string;
}

export interface ErrorDetail {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface ErrorResponse {
  code: string;
  message: string;
  details?: ErrorDetail[];
}

// ── Evaluation Types ──

export interface ScoringTestResult {
  id: string;
  name: string;
  category: string;
  company: string;
  ctc_inr: number;
  expected_range: [number, number];
  actual_score: number;
  grade: string;
  passed: boolean;
  badges: string[];
  risk_factors: string[];
  breakdown: Record<string, { score: number; weight: number }>;
  confidence: number;
}

export interface ScoreDistribution {
  mean: number;
  median: number;
  std_dev: number;
  min_score: number;
  max_score: number;
  q1: number;
  q3: number;
  iqr: number;
  skewness: number;
  kurtosis: number;
  range_span: number;
}

export interface CategoryComparison {
  category_a: string;
  category_b: string;
  mean_a: number;
  mean_b: number;
  std_a: number;
  std_b: number;
  n_a: number;
  n_b: number;
  t_statistic: number;
  p_value_approx: number;
  significant: boolean;
  effect_size: number;
}

export interface CorrelationResult {
  feature: string;
  pearson_r: number;
  direction: string;
  strength: string;
}

export interface EvaluationReport {
  timestamp: string;
  engine_version: string;
  total_test_cases: number;
  evaluation_time_ms: number;

  scoring_pass_rate: number;
  scoring_results: ScoringTestResult[];

  score_distribution: ScoreDistribution;
  grade_distribution: Record<string, number>;
  category_means: Record<string, number>;

  category_comparisons: CategoryComparison[];
  feature_correlations: CorrelationResult[];

  known_ordering_total: number;
  known_ordering_correct: number;
  known_ordering_accuracy: number;

  determinism_runs: number;
  determinism_score: number;

  component_stats: Record<string, { mean: number; std: number; min: number; max: number }>;
}
