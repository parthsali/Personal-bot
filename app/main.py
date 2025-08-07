from services.github_service import GitHubService
from config import Config
import json

github_service = GitHubService(Config.GITHUB_PERSONAL_ACCESS_TOKEN)

data = github_service.fetch_all_detailed_repos()

file_path = "data.json"

with open(file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)