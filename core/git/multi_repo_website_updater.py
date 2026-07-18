"""
Multi-Repository Website Updater for Autonomous Marketing Agent.

Wraps WebsiteUpdater to operate across every repository managed by a
MultiRepoGitManager, so callers (e.g. ProcessOrchestrator) can trigger an
update by repository name or enumerate all managed repositories.
"""

import logging
from typing import Dict, List, Optional, Any

from core.git.multi_repo_git_manager import MultiRepoGitManager
from core.git.website_updater import WebsiteUpdater
from core.analytics.analytics_engine import AnalyticsEngine

logger = logging.getLogger(__name__)


class MultiRepoWebsiteUpdater:
    """
    Coordinates WebsiteUpdater instances across multiple repositories.
    """

    def __init__(self, git_manager: MultiRepoGitManager,
                 analytics_engine: Optional[AnalyticsEngine] = None,
                 config_path: Optional[str] = None):
        """
        Initialize the multi-repository website updater.

        Args:
            git_manager: MultiRepoGitManager providing per-repository GitIntegration instances
            analytics_engine: Shared AnalyticsEngine instance (created if not provided)
            config_path: Path to a WebsiteUpdater config file, applied to every repository
        """
        self.git_manager = git_manager
        self.analytics_engine = analytics_engine or AnalyticsEngine()
        self.config_path = config_path
        self._updaters: Dict[str, WebsiteUpdater] = {}

    def get_all_repository_configs(self) -> List[Dict[str, Any]]:
        """Return the configuration entries for every managed repository."""
        return self.git_manager.get_repository_configs()

    def _get_updater(self, repository_name: str) -> WebsiteUpdater:
        if repository_name not in self._updaters:
            git_integration = self.git_manager.get_git_integration(repository_name)
            if git_integration is None:
                raise ValueError(f"Unknown repository: {repository_name}")
            self._updaters[repository_name] = WebsiteUpdater(
                git_integration, self.analytics_engine, self.config_path
            )
        return self._updaters[repository_name]

    async def update_website(self, repository_name: str) -> Dict[str, Any]:
        """
        Run a full update cycle for the named repository.

        Args:
            repository_name: Name of the repository to update (must be configured)

        Returns:
            Dict with the update status for that repository
        """
        updater = self._get_updater(repository_name)
        success = updater.run_update_cycle()
        return {"status": "success" if success else "error", "repository": repository_name}
