"""
Multi-Repository Git Manager for Autonomous Marketing Agent.

Loads a single configuration file describing multiple repositories (see
core/git/git_config.json for the schema) and provides a GitIntegration
instance per repository, keyed by repository name.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any

from core.git.git_integration import GitIntegration

logger = logging.getLogger(__name__)


class MultiRepoGitManager:
    """
    Manages GitIntegration instances for multiple repositories loaded from
    a shared configuration file.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the multi-repository Git manager.

        Args:
            config_path: Path to a JSON config file with a "repositories" list.
        """
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self._git_integrations: Dict[str, GitIntegration] = {}
        self._build_git_integrations()

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        if not config_path or not os.path.exists(config_path):
            logger.warning(f"Git config not found at {config_path}, no repositories configured")
            return {"repositories": []}

        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading git config from {config_path}: {e}")
            return {"repositories": []}

    def _build_git_integrations(self) -> None:
        auth = self.config.get("auth", {})
        default_username = auth.get("username") or None
        token_env_var = auth.get("token_env_var")
        default_token = os.environ.get(token_env_var) if token_env_var else None

        for repo_cfg in self.config.get("repositories", []):
            name = repo_cfg.get("name")
            if not name:
                logger.warning("Skipping repository entry with no 'name'")
                continue

            repo_url = repo_cfg.get("repo_url") or repo_cfg.get("url")
            if not repo_url:
                logger.warning(f"Skipping repository '{name}': no repo_url/url configured")
                continue

            local_path = repo_cfg.get("local_path", os.path.join("data", "repositories", name))
            branch = repo_cfg.get("default_branch") or repo_cfg.get("branch", "main")

            self._git_integrations[name] = GitIntegration(
                repo_url=repo_url,
                local_path=local_path,
                username=repo_cfg.get("username", default_username),
                token=repo_cfg.get("token", default_token),
                branch=branch
            )

    def list_repositories(self) -> List[str]:
        """Return the names of all configured repositories."""
        return list(self._git_integrations.keys())

    def get_repository_configs(self) -> List[Dict[str, Any]]:
        """Return the raw configuration entries for all repositories."""
        return self.config.get("repositories", [])

    def get_git_integration(self, name: str) -> Optional[GitIntegration]:
        """Return the GitIntegration instance for a given repository name."""
        return self._git_integrations.get(name)
