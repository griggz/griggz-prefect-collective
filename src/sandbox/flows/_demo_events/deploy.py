from prefect import flow
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the OPENAI_API_KEY from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Example usage
if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/griggz/griggz-prefect-collective.git",
        entrypoint="src/sandbox/flows/_demo_events/flow.py:governance_flow",
    ).deploy(
        name="governance-events-flow",
        work_pool_name="managed-pool",
        job_variables={
            "pip_packages": ["prefect", "controlflow", "pydantic"],
            "env": {
                "OPENAI_API_KEY": OPENAI_API_KEY,  # Use the API key here
            },
        },
    )
