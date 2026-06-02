from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTION_PATH = ROOT / ".github" / "actions" / "real-world-erh" / "action.yml"
WORKFLOWS = [
    ROOT / ".github" / "workflows" / "build_thesis_gated.yml",
    ROOT / ".github" / "workflows" / "build_thesis.yml",
    ROOT / ".github" / "workflows" / "single_sh_based_build_thesis.yml",
]


def test_real_world_erh_composite_action_covers_new_cases():
    action = ACTION_PATH.read_text(encoding="utf-8")

    for test_file in [
        "tests/test_content_moderation_case_study.py",
        "tests/test_compas_real_world_extensions.py",
        "tests/test_medical_triage_case_study.py",
        "tests/test_truthfulqa_case_study.py",
        "tests/test_llm_bias_case_study.py",
        "tests/test_erh_case_comparison.py",
    ]:
        assert test_file in action

    for script in [
        "python simulation/real_data/content_moderation_case_study.py",
        "python simulation/real_data/medical_triage_case_study.py",
        "python simulation/real_data/truthfulqa_case_study.py",
        "python simulation/real_data/llm_bias_case_study.py",
        "python simulation/real_data/erh_case_comparison.py",
    ]:
        assert script in action

    assert 'ERH_REAL_WORLD_OFFLINE: "1"' in action


def test_thesis_workflows_use_real_world_erh_composite_action():
    for workflow_path in WORKFLOWS:
        workflow = workflow_path.read_text(encoding="utf-8")
        assert "uses: ./.github/actions/real-world-erh" in workflow, workflow_path.name
