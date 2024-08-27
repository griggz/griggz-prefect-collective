from typing import List

import requests
from core.clients.github_ import GitHubClient
from prefect import flow, task
from pydantic import BaseModel


class PRFileData(BaseModel):
    repo_owner: str
    repo_name: str
    file_name: str
    base_file: str
    pr_content: str


@task(log_prints=True)
def account_valid(name: str, client: GitHubClient):
    url = f"https://api.github.com/users/{name}"
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Account {name} is valid.")
        return True
    else:
        raise ValueError(
            f"Account {name} is not valid. Status code: {response.status_code}"
        )


@task(log_prints=True)
def get_recent_pull_requests_task(username: str, client: GitHubClient):
    return client.get_recent_pull_requests(username)


@task(log_prints=True)
def get_pull_request_files_task(
    owner: str, repo: str, pr_number: int, client: GitHubClient
):
    return client.get_pull_request_files(owner, repo, pr_number)


@task(log_prints=True)
def get_file_content_task(
    owner: str, repo: str, path: str, client: GitHubClient, ref=None
):
    return client.get_file_content(owner, repo, path, ref)


@flow
def fetch_pull_request_files(username: str) -> List[PRFileData]:
    client = GitHubClient()
    result = []

    if account_valid(username, GitHubClient):
        pull_requests = client.get_pull_requests_last_year(username)

        for pr in pull_requests:
            repo_full_name = pr["repository_url"].split("/")[-2:]
            repo_owner, repo_name = repo_full_name[0], repo_full_name[1]
            pr_number = pr["number"]
            pr_files = get_pull_request_files_task(repo_owner, repo_name, pr_number, client)
            for pr_file in pr_files:
                file_path = pr_file["filename"]
                if "README" in file_path.upper():
                    continue
                pr_file_content = get_file_content_task(
                    repo_owner,
                    repo_name,
                    file_path,
                    client,
                    ref=f"refs/pull/{pr_number}/head",
                )
                base_file_content = get_file_content_task(
                    repo_owner, repo_name, file_path, client
                )

                result.append(
                    {
                        "repo_owner": repo_owner,
                        "repo_name": repo_name,
                        "file_name": file_path,
                        "base_file": base_file_content,
                        "pr_content": pr_file_content,
                    }
                )

    return result


if __name__ == "__main__":
    # Example usage
    username = "Samreay"  # Replace with the desired GitHub username
    # Fetch pull request files and content for each pull request
    results = fetch_pull_request_files()
