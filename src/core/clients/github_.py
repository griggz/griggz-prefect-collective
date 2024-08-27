import os
import requests
import base64
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Optional

# Load environment variables from the .env file
load_dotenv()


class GitHubClient:
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token=None):
        if token is None:
            token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("A GitHub token must be provided")
        
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'token {token}'})
    
    def get_public_repos(self, username):
        url = f"{self.BASE_URL}/users/{username}/repos"
        response = self._make_request("GET", url)
        return response.json()
    
    def get_pull_requests(self, owner, repo):
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls?state=all"
        response = self._make_request("GET", url)
        return response.json()

    def get_pull_request_files(self, owner, repo, pr_number):
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        response = self._make_request("GET", url)
        return response.json()
    

    def get_file_content(self, owner, repo, path, ref=None) -> Optional[str]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"
        if ref:
            url += f"?ref={ref}"
        try:
            response = self._make_request("GET", url)
            file_content = response.json()
            if 'content' in file_content:
                return base64.b64decode(file_content['content']).decode('utf-8')
            else:
                print(f"No content found in file {path}")
                return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"File not found: {path} at {url}")
                return None
            else:
                print(f"HTTP error occurred: {str(e)}")
                raise

    
    def get_recent_pull_requests(self, username):
        url = f"{self.BASE_URL}/search/issues?q=author:{username}+type:pr"
        response = self._make_request("GET", url)
        return response.json()["items"]
    
    def get_pull_requests_last_year(self, username):
        one_year_ago = datetime.now() - timedelta(days=730)
        formatted_date = one_year_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
        url = f"{self.BASE_URL}/search/issues?q=author:{username}+type:pr+created:>{formatted_date}"
        response = self._make_request("GET", url)
        return response.json()["items"]

    def _make_request(self, method, url, **kwargs):
        print(f"Making {method} request to {url}")
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            print(f"Request to {url} succeeded with status code {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request to {url} failed: {str(e)}")
            raise
