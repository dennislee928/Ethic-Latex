from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .db import Base


class Action(Base):
    """
    Represents a merge request (MR) or change action extracted from GitLab.
    """

    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(index=True)
    mr_iid: Mapped[int] = mapped_column(index=True)
    title: Mapped[str] = mapped_column(String(512))

    lines_changed: Mapped[int] = mapped_column(Integer, default=0)
    files_changed: Mapped[int] = mapped_column(Integer, default=0)
    services_touched: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    judgment: Mapped["Judgment"] = relationship(back_populates="action", uselist=False)
    ground_truth: Mapped["GroundTruth"] = relationship(back_populates="action", uselist=False)
    importance: Mapped["Importance"] = relationship(back_populates="action", uselist=False)
    derived_metrics: Mapped["DerivedMetrics"] = relationship(back_populates="action", uselist=False)


class Judgment(Base):
    """
    Stores security scan results or human review judgments linked to an Action.
    """

    __tablename__ = "judgments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    action_id: Mapped[int] = mapped_column(ForeignKey("actions.id"), index=True, unique=True)

    judge_type: Mapped[str] = mapped_column(String(32), index=True)  # PIPELINE / HUMAN / COMBINED
    pipeline_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    human_review_status: Mapped[str | None] = mapped_column(String(32), nullable=True)

    findings_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    action: Mapped[Action] = relationship(back_populates="judgment")


class GroundTruth(Base):
    """
    Represents an approximation of the true security state for an Action.
    """

    __tablename__ = "ground_truth"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    action_id: Mapped[int] = mapped_column(ForeignKey("actions.id"), index=True, unique=True)

    unresolved_high_count: Mapped[int] = mapped_column(Integer, default=0)
    post_incident_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    incident_severity: Mapped[str | None] = mapped_column(String(32), nullable=True)

    action: Mapped[Action] = relationship(back_populates="ground_truth")


class Importance(Base):
    """
    Captures asset criticality and exposure for a given Action.
    """

    __tablename__ = "importance"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    action_id: Mapped[int] = mapped_column(ForeignKey("actions.id"), index=True, unique=True)

    asset_criticality: Mapped[int] = mapped_column(Integer, default=1)  # e.g., 1–5
    internet_exposed: Mapped[bool] = mapped_column(Boolean, default=False)
    service_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    action: Mapped[Action] = relationship(back_populates="importance")


class DerivedMetrics(Base):
    """
    Cached ERH-style metrics for each Action.
    """

    __tablename__ = "derived_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    action_id: Mapped[int] = mapped_column(ForeignKey("actions.id"), index=True, unique=True)

    complexity: Mapped[float] = mapped_column(Float, default=1.0)
    ground_truth_value: Mapped[float] = mapped_column(Float, default=0.0)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    judgment_value: Mapped[float] = mapped_column(Float, default=0.0)

    delta: Mapped[float] = mapped_column(Float, default=0.0)
    is_mistake: Mapped[bool] = mapped_column(Boolean, default=False)
    is_prime: Mapped[bool] = mapped_column(Boolean, default=False)

    action: Mapped[Action] = relationship(back_populates="derived_metrics")


