export interface LatexRule {
  id: number
  title: string
  content: string
  owner_id: number
  created_at: string
  updated_at: string
  is_active: boolean
}

export interface LatexRuleCreate {
  title: string
  content: string
}

export interface LatexRuleUpdate {
  title?: string
  content?: string
  is_active?: boolean
}

export interface ValidationResult {
  rule_id: number
  risk_score: number
  violations: Violation[]
  verified_at: string
}

export interface Violation {
  type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  line?: number
  column?: number
}

