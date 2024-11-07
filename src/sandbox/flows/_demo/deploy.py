from prefect import flow
from prefect_github import GitHubRepository
import os

if __name__ == "__main__":
    with open('requirements.txt', 'r') as file:
        requirements = file.read().splitlines()

    # Create a GitHub repository object
    github_repo = GitHubRepository(
        repository="https://github.com/griggz/griggz-prefect-collective.git",
        reference="main"  # or whichever branch you're using
    )

    # Deploy the flow
    flow.from_source(
        source=github_repo,
        entrypoint="sandbox/flows/_demo/flow.py:take_a_walk",
    ).deploy(
        name="take-a-walk-demo",
        work_pool_name="default",
        job_variables={"pip_packages": requirements}
    )
