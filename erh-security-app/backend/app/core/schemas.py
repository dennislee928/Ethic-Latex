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


