"""
API routes for LaTeX rules management.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.schemas import LatexRuleCreate, LatexRuleUpdate, LatexRuleRead
from ..core.models import LatexRule
from ..deps import get_db, get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=LatexRuleRead, tags=["rules"])
def create_rule(
    rule: LatexRuleCreate,
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_current_user_id),
):
    """
    Create a new LaTeX rule.

    VUL-003: owner_id is resolved from the authenticated user via
    get_current_user_id(). Full JWT validation is pending (see deps.py).
    """
    logger.info("Creating rule for user_id=%d title=%r", owner_id, rule.title)
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
    user_id: int = Depends(get_current_user_id),
):
    """List LaTeX rules owned by the authenticated user."""
    # VUL-003: Filter by authenticated user to prevent cross-user data access.
    rules = (
        db.query(LatexRule)
        .filter(LatexRule.owner_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return rules


@router.get("/{rule_id}", response_model=LatexRuleRead, tags=["rules"])
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get a specific LaTeX rule by ID (must be owned by authenticated user)."""
    # VUL-003: Combine id + owner filter to prevent access to other users' rules.
    rule = (
        db.query(LatexRule)
        .filter(LatexRule.id == rule_id, LatexRule.owner_id == user_id)
        .first()
    )
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=LatexRuleRead, tags=["rules"])
def update_rule(
    rule_id: int,
    rule_update: LatexRuleUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update an existing LaTeX rule (must be owned by authenticated user)."""
    # VUL-003: Ownership enforced via combined filter.
    rule = (
        db.query(LatexRule)
        .filter(LatexRule.id == rule_id, LatexRule.owner_id == user_id)
        .first()
    )
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    if rule_update.title is not None:
        rule.title = rule_update.title
    if rule_update.content is not None:
        rule.content = rule_update.content
    if rule_update.is_active is not None:
        rule.is_active = rule_update.is_active

    db.commit()
    db.refresh(rule)
    logger.info("Updated rule id=%d for user_id=%d", rule_id, user_id)
    return rule


@router.delete("/{rule_id}", tags=["rules"])
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete a LaTeX rule (must be owned by authenticated user)."""
    # VUL-003: Ownership enforced via combined filter.
    rule = (
        db.query(LatexRule)
        .filter(LatexRule.id == rule_id, LatexRule.owner_id == user_id)
        .first()
    )
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.delete(rule)
    db.commit()
    logger.info("Deleted rule id=%d for user_id=%d", rule_id, user_id)
    return {"message": "Rule deleted successfully"}

