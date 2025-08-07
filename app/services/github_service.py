import requests
import os
import time
import base64
from config import Config

class GitHubService:
    def __init__(self, GITHUB_PERSONAL_ACCESS_TOKEN):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {GITHUB_PERSONAL_ACCESS_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.session = requests.Session()

    def _fetch_paginated_data(self, url):
        """Internal method to handle paginated API requests."""
        all_data = []
        while url:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            all_data.extend(response.json())

            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None
        return all_data

    def _get_all_user_repos(self):
        """Fetches all repositories for the authenticated user."""
        repos_url = f"{self.base_url}/user/repos?type=owner&per_page=100"
        return self._fetch_paginated_data(repos_url)

    def _get_repo_details(self, owner, repo_name):
        """Fetches detailed data for a specific repository."""
        details_url = f"{self.base_url}/repos/{owner}/{repo_name}"
        response = self.session.get(details_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def _get_repo_readme(self, owner, repo_name):
        """
        Fetches the README.md content for a repository.
        Returns decoded text or None if no README is found.
        """
        readme_url = f"{self.base_url}/repos/{owner}/{repo_name}/readme"
        try:
            response = self.session.get(readme_url, headers=self.headers)
            response.raise_for_status()

            # The content is returned as a Base64 encoded string
            content = response.json()['content']
            # Decode the Base64 string to a human-readable format
            decoded_content = base64.b64decode(content).decode('utf-8')
            return decoded_content
        except requests.exceptions.HTTPError as e:
            # A 404 error means the README file doesn't exist
            if e.response.status_code == 404:
                return None
            else:
                raise e # Re-raise other HTTP errors
        except Exception as e:
            print(f"An error occurred fetching README for {owner}/{repo_name}: {e}")
            return None

    def fetch_all_detailed_repos(self):
        """Combines fetching all repos with fetching details for each."""
        all_repos = self._get_all_user_repos()
        all_detailed_repos = []

        for repo in all_repos:
            time.sleep(0.5)
            
            owner = repo['owner']['login']
            repo_name = repo['name']
            
            try:
                # Fetch detailed data
                detailed_data = self._get_repo_details(owner, repo_name)
                readme_content = self._get_repo_readme(owner, repo_name)
                
                if detailed_data['private'] and readme_content is None:
                    continue
                    
                # Fetch README content
                
                selected_fields = [
                    'id', 'name', 'name', 'html_url', 'description', 
                    'readme_content', 'stargazers_count', 'private'
                ]
                
                

            
                selective_repo_data = {
                    field: detailed_data.get(field) for field in selected_fields
                }
                
    
                
                if readme_content:
                    selective_repo_data['readme_content'] = readme_content
                else:
                    selective_repo_data['readme_content'] = "No README found."

                # Append the new, selective dictionary to your list
                all_detailed_repos.append(selective_repo_data)
                print(f"Fetched details and README for {owner}/{repo_name}")
            except requests.HTTPError as e:
                print(f"Failed to fetch details for {owner}/{repo_name}: {e}")

        return all_detailed_repos