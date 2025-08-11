"""
# Deploy a flow using Docker

This example shows how to deploy a flow in a Prefect built Docker image.
It assumes you have a work pool named `docker`. You can implicitly create the
work pool by starting a worker:

```bash
prefect worker start --pool docker --type docker
```
"""

import subprocess

from dotenv import dotenv_values
from prefect.docker import DockerImage
from prefect.events import DeploymentEventTrigger

from src.sandbox.flows._demo_webhooks.flow import sandbox_club_creation

REGISTRY_URL = "prefectregistry.azurecr.io"
IMAGE_NAME = "sandbox-image"


def get_deployment_env():
    """Get all environment variables for deployment"""
    # Get .env file variables
    env_vars = dotenv_values("src/sandbox/.env")

    # Add Prefect and system variables
    env_config = {
        "PREFECT_LOGGING_LEVEL": "DEBUG",
        "PYTHONPATH": "/opt/prefect/FoundationFlow:${PYTHONPATH}",
        "PREFECT_LOGGING_EXTRA_LOGGERS": "['src']",
        "PREFECT_LOGGING_TO_STDOUT": "true",
        "ENV": "LIVE",
        **env_vars,
    }

    return env_config


def get_image_tag():
    """Return the current git sha if available else latest"""
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError:
        return "latest"


def deploy():
    # Get environment variables
    env_vars = get_deployment_env()
    # Deploy flow
    sandbox_club_creation.deploy(
        name="sandbox-club-creation",
        work_pool_name="aci-pool",
        tags=["sandbox", "webhooks"],
        image=DockerImage(
            name=f"{REGISTRY_URL}/{IMAGE_NAME}",
            tag=get_image_tag(),
            dockerfile="src/sandbox/Dockerfile",
            platform="linux/amd64",
        ),
        build=True,
        push=True,
        job_variables={
            "env": env_vars,
            "streaming_logs": True,
            "azure_container_instance_config": {"region_name": "eastus2"},
        },
        triggers=[
            DeploymentEventTrigger(
                enabled=True,
                match={"prefect.resource.id": "New Club Received"},
                expect=["*"],
                parameters={"form_response": "{{ event.payload|tojson }}"},
                posture="Reactive",
            )
        ],
    )


if __name__ == "__main__":
    deploy()
