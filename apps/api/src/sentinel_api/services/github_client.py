import structlog
import httpx
from typing import Dict, Any, List, Optional
import datetime

logger = structlog.get_logger("sentinel_api.services.github_client")

class GithubClient:
    """Wrapper around GitHub REST API for syncing deployments and code."""
    
    BASE_URL = "https://api.github.com"

    def __init__(self, access_token: str):
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}{path}"
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    async def _post(self, path: str, payload: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}{path}"
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository metadata."""
        return await self._get(f"/repos/{owner}/{repo}")

    async def get_commits(self, owner: str, repo: str, since: Optional[datetime.datetime] = None) -> List[Dict[str, Any]]:
        """Fetch repository commits."""
        params = {}
        if since:
            params["since"] = since.isoformat()
            
        commits = await self._get(f"/repos/{owner}/{repo}/commits", params=params)
        
        # GitHub's list commits API doesn't include lines added/deleted.
        # For a full sync, we would need to fetch each commit individually, but for now we rely on webhooks
        # or just return the basic list.
        return commits

    async def get_commit(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """Fetch a single commit with detailed file changes (stats)."""
        return await self._get(f"/repos/{owner}/{repo}/commits/{sha}")

    async def get_pull_requests(self, owner: str, repo: str, state: str = "all") -> List[Dict[str, Any]]:
        """Fetch repository pull requests."""
        return await self._get(f"/repos/{owner}/{repo}/pulls", params={"state": state})

    async def get_deployments(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch repository deployments."""
        return await self._get(f"/repos/{owner}/{repo}/deployments")
        
    async def get_deployment_statuses(self, owner: str, repo: str, deployment_id: int) -> List[Dict[str, Any]]:
        """Fetch statuses for a specific deployment."""
        return await self._get(f"/repos/{owner}/{repo}/deployments/{deployment_id}/statuses")

    # --- Destructive / Write Methods for Remediation ---

    async def create_branch(self, owner: str, repo: str, branch_name: str, sha: str) -> Dict[str, Any]:
        """Create a new branch pointing to the given SHA."""
        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": sha
        }
        return await self._post(f"/repos/{owner}/{repo}/git/refs", payload=payload)

    async def create_pull_request(self, owner: str, repo: str, title: str, head: str, base: str, body: str, draft: bool = True) -> Dict[str, Any]:
        """Create a new pull request."""
        payload = {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "draft": draft
        }
        return await self._post(f"/repos/{owner}/{repo}/pulls", payload=payload)
