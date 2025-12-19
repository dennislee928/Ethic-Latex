"""
API routes for LaTeX rules management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.schemas import LatexRuleCreate, LatexRuleUpdate, LatexRuleRead
from ..core.models import LatexRule
from ..deps import get_db

router = APIRouter()


@router.post("/", response_model=LatexRuleRead, tags=["rules"])
def create_rule(
    rule: LatexRuleCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new LaTeX rule.
    
    Note: In a production system, you'd get the user_id from authentication.
    For now, we'll use a default user_id of 1.
    """
    # TODO: Get user_id from authenticated user
    owner_id = 1

    db_rule = LatexRule(
        title=rule.title,
        content=rule.content,
        owner_id=owner_id,
        is_active=rule.is_active,
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.get("/", response_model=List[LatexRuleRead], tags=["rules"])
def list_rules(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all LaTeX rules."""
    # TODO: Filter by authenticated user
    rules = db.query(LatexRule).offset(skip).limit(limit).all()
    return rules


@router.get("/{rule_id}", response_model=LatexRuleRead, tags=["rules"])
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific LaTeX rule by ID."""
    rule = db.query(LatexRule).filter(LatexRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=LatexRuleRead, tags=["rules"])
def update_rule(
    rule_id: int,
    rule_update: LatexRuleUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing LaTeX rule."""
    rule = db.query(LatexRule).filter(LatexRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # TODO: Check ownership/authorization

    if rule_update.title is not None:
        rule.title = rule_update.title
    if rule_update.content is not None:
        rule.content = rule_update.content
    if rule_update.is_active is not None:
        rule.is_active = rule_update.is_active

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", tags=["rules"])
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
):
    """Delete a LaTeX rule."""
    rule = db.query(LatexRule).filter(LatexRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # TODO: Check ownership/authorization

    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted successfully"}

