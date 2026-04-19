import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def test_public_thesis_entrypoints_do_not_contain_review_regressions() -> None:
    strict_markers = [
        "[TBD]",
        "[YES/NO]",
        "[Observation",
        "[figure pending]",
        "Run simulation with",
        "This section will be filled",
        "待填入",
        "由模擬管線自動填入",
        "Section ??",
        "Table ??",
        r"\Pi( )",
        "elementsofai.com/zh",
        "conservative judges display r...",
    ]

    bilingual_markers = [
        "[figure pending]",
        "［圖示待補］",
        "待填入",
        "由模擬管線自動填入",
        "Section ??",
        "Table ??",
        r"\Pi( )",
        "elementsofai.com/zh",
        "conservative judges display r...",
        "run pipeline",
    ]

    for relative_path, markers in [
        ("latex/ethical_riemann_hypothesis.tex", strict_markers),
        ("latex/ethical_riemann_hypothesis_en.tex", bilingual_markers),
        ("latex/ethical_riemann_hypothesis_zh.tex", bilingual_markers),
    ]:
        text = _read(relative_path)
        for marker in markers:
            assert marker not in text, f"{relative_path} still contains review marker: {marker}"


def test_local_build_script_copies_quantum_png_assets() -> None:
    build_script = _read("scripts/build_thesis.sh")

    assert "latest_quantum_circuit.png" in build_script
    assert "latest_quantum_distribution.png" in build_script


def test_pdf_text_snapshot_exporter_extracts_key_passages(tmp_path: Path) -> None:
    output_dir = tmp_path / "pdf_text_snapshots"

    subprocess.run(
        ["bash", str(ROOT / "scripts" / "export_pdf_text_snapshots.sh"), str(output_dir)],
        check=True,
        cwd=ROOT,
    )

    en_full = (output_dir / "ethical_riemann_hypothesis_en.full.txt").read_text(encoding="utf-8")
    en_excerpt = (output_dir / "ethical_riemann_hypothesis_en.key_excerpts.md").read_text(encoding="utf-8")
    zh_full = (output_dir / "ethical_riemann_hypothesis_zh.full.txt").read_text(encoding="utf-8")
    zh_excerpt = (output_dir / "ethical_riemann_hypothesis_zh.key_excerpts.md").read_text(encoding="utf-8")
    en_excerpt_normalized = _normalize_whitespace(en_excerpt)
    zh_excerpt_normalized = _normalize_whitespace(zh_excerpt)

    assert "Π(x)" in en_full
    assert "Jobin et al." in en_excerpt_normalized
    assert "Floridi et al., 2018" in en_excerpt_normalized
    assert "Dynamically generated quantum circuit" in en_excerpt

    assert "Π(x)" in zh_full
    assert "B(x)" in zh_full
    assert "動態產生的量子電路" in zh_excerpt
    assert "Jobin et al." in zh_excerpt_normalized
