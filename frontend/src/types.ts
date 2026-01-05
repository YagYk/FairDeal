export interface ContractMetadata {
  contractType: string
  industry: string
  role: string
  location: string
  salary: number
  noticePeriodDays: number
  nonCompete: boolean
}

export interface PercentileRankings {
  salary: number
  noticePeriod: number
  [key: string]: number
}

export interface NegotiationScript {
  clause: string
  script: string
  successProbability: number
}

export interface DetailedExplanation {
  data_sources?: {
    knowledge_base_contracts_used: number
    total_contracts_in_knowledge_base: number
    similar_contracts_details: Array<{
      contract_id: string
      similarity_score: number
      contract_type?: string
      industry?: string
      role?: string
    }>
    data_quality: {
      sample_size: number
      coverage: string
      relevance: string
    }
  }
  explanations?: {
    fairness_score_explanation?: {
      score: number
      category: string
      explanation: string
      factors: string[]
      calculation_method: string
    }
    percentile_explanations?: {
      [key: string]: {
        your_value: string
        percentile: number
        market_comparison: {
          median: string
          mean: string
          p25: string
          p75: string
        }
        explanation: string
      }
    }
    red_flags_explanations?: Array<{
      flag_number: number
      issue: string
      explanation: string
      severity: string
      recommendation: string
    }>
    favorable_terms_explanations?: Array<{
      term_number: number
      term: string
      explanation: string
      value: string
    }>
    negotiation_recommendations?: {
      should_negotiate: boolean
      recommendations: Array<{
        item: string
        current: string
        recommended: string
        reason: string
        priority: string
      }>
      overall_advice: string
    }
    overall_assessment?: {
      assessment: string
      summary: string
      signing_recommendation: string
    }
  }
  confidence_metrics?: {
    confidence_level: string
    sample_size: number
    data_quality: string
    explanation: string
  }
}

export interface AnalysisResult {
  fairnessScore: number
  contractMetadata: ContractMetadata
  percentileRankings: PercentileRankings
  redFlags: (string | { issue?: string; title?: string; explanation?: string })[]
  favorableTerms: (string | { term?: string; title?: string; explanation?: string })[]
  negotiationPriorities: (string | { priority?: string; reason?: string })[]
  negotiationScripts: NegotiationScript[]
  similarContractsCount?: number
  similarContractsDetails?: Array<{
    contract_id: string
    similarity_score: number
    contract_type?: string
    industry?: string
  }>
  detailedExplanation?: DetailedExplanation
}

