from app.core.models import LatexRule, SecurityReport, User


def test_verify_rule_by_id_returns_validation_result_and_persists_report(client, db_session) -> None:
    user = User(email="owner@example.com", hashed_password="not-a-real-hash")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    rule = LatexRule(
        title="Block bypass directives",
        content=r"\textbf{Do not use \bypass in security-sensitive rules}",
        owner_id=user.id,
        is_active=True,
    )
    db_session.add(rule)
    db_session.commit()
    db_session.refresh(rule)

    response = client.post(f"/api/v1/verify/rule/{rule.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["rule_id"] == rule.id
    assert payload["is_valid"] is False
    assert payload["violations"]

    report = db_session.query(SecurityReport).filter(SecurityReport.rule_id == rule.id).first()
    assert report is not None
    assert report.risk_score >= 0.9

