import requests
import base64
import time
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    """
    A service for interacting with the GitHub API to fetch repository data.
    """
    def __init__(self, access_token: str):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.session = requests.Session()

    def _fetch_paginated_data(self, url: str) -> list:
        """
        Handles paginated requests to the GitHub API.
        """
        all_data = []
        while url:
            try:
                response = self.session.get(url, headers=self.headers)
                response.raise_for_status()
                all_data.extend(response.json())
                url = response.links.get('next', {}).get('url')
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching paginated data from {url}: {e}", exc_info=True)
                break
        return all_data

    def _get_all_user_repos(self) -> list:
        """
        Fetches all repositories for the authenticated user.
        """
        repos_url = f"{self.base_url}/user/repos?type=owner&per_page=100"
        logger.info("Fetching all user repositories...")
        repos = self._fetch_paginated_data(repos_url)
        logger.info(f"Found {len(repos)} repositories.")
        return repos

    def _get_repo_readme(self, owner: str, repo_name: str) -> str:
        """
        Fetches the README content for a specific repository.
        """
        readme_url = f"{self.base_url}/repos/{owner}/{repo_name}/readme"
        try:
            response = self.session.get(readme_url, headers=self.headers)
            response.raise_for_status()
            content = response.json()['content']
            return base64.b64decode(content).decode('utf-8')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"No README found for {owner}/{repo_name}.")
            else:
                logger.error(f"HTTP error fetching README for {owner}/{repo_name}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"An unexpected error occurred fetching README for {owner}/{repo_name}: {e}", exc_info=True)
        return "No README found."


    def fetch_all_detailed_repos(self) -> list:
        """
        Fetches detailed information and READMEs for all user repositories.
        """
        all_repos = self._get_all_user_repos()
        detailed_repos = []

        for repo in all_repos:
            time.sleep(0.5)  # To avoid hitting rate limits
            owner = repo['owner']['login']
            repo_name = repo['name']
            logger.info(f"Fetching details for repository: {owner}/{repo_name}")

            try:
                readme_content = self._get_repo_readme(owner, repo_name)

                repo_data = {
                    "name": repo.get("name", "N/A"),
                    "description": repo.get("description", "N/A"),
                    "html_url": repo.get("html_url", "N/A"),
                    "stargazers_count": repo.get("stargazers_count", "N/A"),
                    "private": repo.get("private", "N/A"),
                    "readme_content": readme_content,
                }
                detailed_repos.append(repo_data)
                logger.info(f"Successfully fetched details for {owner}/{repo_name}")
            except Exception as e:
                logger.error(f"Failed to fetch details for {owner}/{repo_name}: {e}", exc_info=True)

        return detailed_repos