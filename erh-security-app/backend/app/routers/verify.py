"""
API routes for LaTeX rule verification.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from ..core.schemas import ValidationResult, Violation
from ..core.models import LatexRule, SecurityReport
from ..services.erh_service import verify_latex_rule, analyze_rule_security
from ..deps import get_db

router = APIRouter()


class VerifyRequest(BaseModel):
    latex_content: str


def _verify_latex_content(
    latex_content: str,
    *,
    rule_id: int | None,
    db: Session,
) -> ValidationResult:
    if not latex_content:
        raise HTTPException(status_code=400, detail="LaTeX content cannot be empty")

    verification_result = verify_latex_rule(latex_content)

    violations = [
        Violation(
            type=v.get("type", "unknown"),
            severity=v.get("severity", "medium"),
            message=v.get("message", ""),
            line=v.get("line"),
            column=v.get("column"),
        )
        for v in verification_result.get("violations", [])
    ]

    if rule_id is not None:
        rule = db.query(LatexRule).filter(LatexRule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")

        report = db.query(SecurityReport).filter(SecurityReport.rule_id == rule_id).first()
        if report:
            report.risk_score = verification_result["risk_score"]
            report.violations = {
                "violations": [v.dict() for v in violations],
                "warnings": verification_result.get("warnings", []),
            }
            report.verified_at = datetime.utcnow()
        else:
            report = SecurityReport(
                rule_id=rule_id,
                risk_score=verification_result["risk_score"],
                violations={
                    "violations": [v.dict() for v in violations],
                    "warnings": verification_result.get("warnings", []),
                },
            )
            db.add(report)

        db.commit()

    return ValidationResult(
        rule_id=rule_id or 0,
        risk_score=verification_result["risk_score"],
        violations=violations,
        verified_at=datetime.utcnow(),
        is_valid=verification_result.get("is_valid", False),
        warnings=verification_result.get("warnings", []),
    )


@router.post("/", response_model=ValidationResult, tags=["verify"])
def verify_rule(
    request: VerifyRequest,
    rule_id: int | None = None,
    db: Session = Depends(get_db),
):
    """
    Verify a LaTeX rule string against ethical security constraints.
    
    Args:
        request: Request body containing latex_content
        rule_id: Optional rule ID to associate verification with
    """
    return _verify_latex_content(
        request.latex_content,
        rule_id=rule_id,
        db=db,
    )


@router.post("/rule/{rule_id}", response_model=ValidationResult, tags=["verify"])
def verify_rule_by_id(
    rule_id: int,
    db: Session = Depends(get_db),
):
    """Verify an existing rule by its ID."""
    rule = db.query(LatexRule).filter(LatexRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    return _verify_latex_content(rule.content, rule_id=rule_id, db=db)


@router.get("/rule/{rule_id}/validate", response_model=ValidationResult, tags=["verify"])
def get_validation_result(
    rule_id: int,
    db: Session = Depends(get_db),
):
    """Get the latest validation result for a rule."""
    rule = db.query(LatexRule).filter(LatexRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    report = db.query(SecurityReport).filter(SecurityReport.rule_id == rule_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="No validation result found for this rule")

    violations_data = report.violations or {}
    violations_list = violations_data.get("violations", [])

    violations = [
        Violation(
            type=v.get("type", "unknown"),
            severity=v.get("severity", "medium"),
            message=v.get("message", ""),
            line=v.get("line"),
            column=v.get("column"),
        )
        for v in violations_list
    ]

    return ValidationResult(
        rule_id=rule_id,
        risk_score=report.risk_score,
        violations=violations,
        verified_at=report.verified_at,
        is_valid=report.risk_score < 0.5,  # Simplified: low risk = valid
        warnings=violations_data.get("warnings", []),
    )
