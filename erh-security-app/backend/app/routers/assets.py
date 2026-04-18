from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parents[4]
FIGURE_DIRECTORIES = (
    ("figures", PROJECT_ROOT / "figures"),
    ("simulation", PROJECT_ROOT / "simulation" / "output" / "figures"),
)


def _build_asset(relative_path: Path, category: str) -> dict:
    return {
        "name": relative_path.name,
        "category": category,
        "relative_path": relative_path.as_posix(),
        "url": f"/assets/files/{relative_path.as_posix()}",
    }


def _resolve_project_path(relative_path: str) -> Path:
    candidate = (PROJECT_ROOT / relative_path).resolve()

    try:
        candidate.relative_to(PROJECT_ROOT.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Asset not found") from exc

    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Asset not found")

    return candidate


@router.get("/index", tags=["assets"])
def get_asset_index() -> dict:
    documents = [
        _build_asset(path.relative_to(PROJECT_ROOT), "document")
        for path in sorted(PROJECT_ROOT.glob("*.pdf"))
    ]

    figures: list[dict] = []
    for category, directory in FIGURE_DIRECTORIES:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.pdf")):
            figures.append(_build_asset(path.relative_to(PROJECT_ROOT), category))

    return {
        "documents": documents,
        "figures": figures,
    }


@router.get("/files/{relative_path:path}", tags=["assets"])
def get_asset_file(relative_path: str) -> FileResponse:
    asset_path = _resolve_project_path(relative_path)
    return FileResponse(asset_path)
