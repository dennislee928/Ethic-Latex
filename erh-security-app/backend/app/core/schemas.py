from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ActionBase(BaseModel):
    project_id: int
    mr_iid: int
    title: str
    lines_changed: int = 0
    files_changed: int = 0
    services_touched: int = 0


class ActionRead(ActionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class JudgmentBase(BaseModel):
    judge_type: str
    pipeline_status: Optional[str] = None
    human_review_status: Optional[str] = None
    findings_json: Optional[dict] = None


class JudgmentRead(JudgmentBase):
    id: int
    action_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class GroundTruthBase(BaseModel):
    unresolved_high_count: int = 0
    post_incident_flag: bool = False
    incident_severity: Optional[str] = None


class GroundTruthRead(GroundTruthBase):
    id: int
    action_id: int

    class Config:
        orm_mode = True


class ImportanceBase(BaseModel):
    asset_criticality: int = 1
    internet_exposed: bool = False
    service_name: Optional[str] = None


class ImportanceRead(ImportanceBase):
    id: int
    action_id: int

    class Config:
        orm_mode = True


class DerivedMetricsRead(BaseModel):
    id: int
    action_id: int
    complexity: float
    ground_truth_value: float
    weight: float
    judgment_value: float
    delta: float
    is_mistake: bool
    is_prime: bool

    class Config:
        orm_mode = True


class AnalysisSummary(BaseModel):
    judge_type: str
    num_samples: int
    num_primes: int
    estimated_alpha: float | None = None
    r_squared: float | None = None


class CurvePoint(BaseModel):
    x: float
    y: float


class AnalysisCurves(BaseModel):
    pi_curve: list[CurvePoint]
    error_curve: list[CurvePoint]


class HeatmapCell(BaseModel):
    complexity_bin: float
    delta_mean: float
    count: int


class HeatmapResponse(BaseModel):
    judge_type: str
    cells: list[HeatmapCell]


# LaTeX Rules Schemas
class LatexRuleBase(BaseModel):
    title: str
    content: str
    is_active: bool = True


class LatexRuleCreate(LatexRuleBase):
    pass


class LatexRuleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None


class LatexRuleRead(LatexRuleBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Verification Schemas
class Violation(BaseModel):
    type: str
    severity: str
    message: str
    line: Optional[int] = None
    column: Optional[int] = None


class ValidationResult(BaseModel):
    rule_id: int
    risk_score: float
    violations: list[Violation]
    verified_at: datetime
    is_valid: bool
    warnings: list[str] = []


# Simulation Schemas
class SimulationConfig(BaseModel):
    num_actions: int = 1000
    complexity_dist: str = "zipf"
    tau: float = 0.3


class SimulationAnalysis(BaseModel):
    estimated_exponent: float
    alpha_ci_low: float
    alpha_ci_high: float
    erh_satisfied: bool
    r_squared: float
    growth_rate: str


class SimulationResult(BaseModel):
    mistake_rate: float
    ethical_primes_count: int
    analysis: SimulationAnalysis
    config: SimulationConfig


class SimulationCreate(BaseModel):
    num_actions: int = 1000
    complexity_dist: str = "zipf"
    tau: float = 0.3


class SimulationRead(BaseModel):
    id: int
    status: str
    result_path: Optional[str] = None
    config: dict
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Security Report Schemas
class SecurityReportRead(BaseModel):
    id: int
    rule_id: int
    risk_score: float
    violations: Optional[dict] = None
    verified_at: datetime

    class Config:
        from_attributes = True


# Settings Schemas
class UserPreferences(BaseModel):
    theme: str = "light"
    default_judge_type: str = "COMBINED"
    auto_save: bool = True
    api_base_url: Optional[str] = None


class UserSettingsRead(BaseModel):
    id: int
    user_id: int
    preferences: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_rules: int
    active_rules: int
    pass_rate: float
    total_violations: int
    critical_violations: int


class ActivityLog(BaseModel):
    id: int
    timestamp: datetime
    type: str
    message: str
    severity: str


