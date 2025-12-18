from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class GitLabClientError(RuntimeError):
    """Generic error raised by GitLabClient."""


@dataclass
class GitLabClient:
    """
    Minimal GitLab API client using Python stdlib only.

    This is intentionally small and opinionated for the PoC. It supports only
    the subset of endpoints we need for building ERH-on-Security datasets.
    """

    base_url: str
    token: Optional[str] = None
    timeout: int = 10

    def _build_url(self, path: str, params: Optional[Dict[str, Any]] = None) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            url = path
        else:
            url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        if params:
            query = urlencode(params)
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}{query}"
        return url

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = self._build_url(path, params)
        headers = {"Accept": "application/json"}
        if self.token:
            # GitLab personal access token header
            headers["PRIVATE-TOKEN"] = self.token

        req = Request(url, method=method.upper(), headers=headers)

        try:
            with urlopen(req, timeout=self.timeout) as resp:
                content_type = resp.headers.get("Content-Type", "")
                data = resp.read()
        except HTTPError as exc:
            # Avoid leaking token or internal details
            raise GitLabClientError(f"GitLab API error {exc.code} for {url}") from exc
        except URLError as exc:
            raise GitLabClientError(f"GitLab API connection error for {url}") from exc

        if "application/json" in content_type:
            return json.loads(data.decode("utf-8"))
        # Fallback: try to parse JSON anyway
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            return data.decode("utf-8")

    # Public methods

    def list_projects(self, membership: bool = True, per_page: int = 50) -> List[Dict[str, Any]]:
        """
        List projects visible to the token.
        """
        params: Dict[str, Any] = {"per_page": per_page}
        if membership:
            params["membership"] = "true"
        result = self._request("GET", "/api/v4/projects", params)
        return list(result or [])

    def list_merge_requests(
        self,
        project_id: int,
        state: str = "merged",
        updated_after: Optional[str] = None,
        per_page: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        List merge requests for a project.

        updated_after: ISO-8601 timestamp string, e.g. '2024-01-01T00:00:00Z'
        """
        params: Dict[str, Any] = {
            "state": state,
            "per_page": per_page,
            "with_merge_status_recheck": "true",
        }
        if updated_after:
            params["updated_after"] = updated_after

        path = f"/api/v4/projects/{project_id}/merge_requests"
        result = self._request("GET", path, params)
        return list(result or [])

    def get_pipelines_for_mr(self, project_id: int, mr_iid: int) -> List[Dict[str, Any]]:
        """
        Get pipelines associated with a merge request.
        """
        path = f"/api/v4/projects/{project_id}/merge_requests/{mr_iid}/pipelines"
        result = self._request("GET", path)
        return list(result or [])

    def get_pipeline(self, project_id: int, pipeline_id: int) -> Dict[str, Any]:
        path = f"/api/v4/projects/{project_id}/pipelines/{pipeline_id}"
        result = self._request("GET", path)
        return dict(result or {})

    def get_security_reports(self, project_id: int, pipeline_id: int) -> Dict[str, Any]:
        """
        Fetch security reports for a pipeline.

        This uses GitLab's security report endpoint, which may require
        appropriate licensing and configuration. For environments where this is
        not available, this method may simply return an empty dict.
        """
        path = f"/api/v4/projects/{project_id}/pipelines/{pipeline_id}/security/report"
        result = self._request("GET", path)
        return dict(result or {})


