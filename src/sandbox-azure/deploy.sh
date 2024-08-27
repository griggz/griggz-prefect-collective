#!/bin/bash

# Ensure the script stops on first error
set -e

WORKER_NAME=sandbox-worker
IMAGE_BASE_NAME=sandbox-image
IMAGE_TAG=$(date +%Y%m%d)-$(date +%H%M)
IMAGE_NAME=$IMAGE_BASE_NAME:$IMAGE_TAG
CONTAINER_PREFIX=sandbox-flows-container
CONTAINER_NAME=$CONTAINER_PREFIX-$IMAGE_TAG
RESOURCE_GROUP=prefect-agents

# Read environment variables from .env file
echo "Building ENV VARS"
ENV_VARS=$(awk -F '=' '/^[^#]/ {
    value = $2;
    for (i = 3; i <= NF; i++) value = value "=" $i;
    print "", $1 "=" value
}' flows/sandbox-azure/.env | xargs)
ENV_VARS+=" ENV=LIVE"

echo "Cleaning up container instances..."
REGISTRY_PW=$(grep 'AZURE_CONTAINER_REGISTRY_PW' flows/sandbox-azure/.env | cut -d '=' -f2)

containers=$(az container list --resource-group $RESOURCE_GROUP --query "[].name" --output tsv)
regex="^${CONTAINER_PREFIX}-[0-9]{8}-[0-9]{4}$"

for container in $containers; do
  if [[ $container =~ $regex ]]; then
    echo "Deleting container $container..."
    az container delete --name $container --resource-group $RESOURCE_GROUP --yes
  else
    echo "Skipping container $container, does not match pattern."
  fi
done

echo "Logging into Azure..."
az acr login --name prefectcontainers
echo "Building new image from local Dockerfile..."
az acr build --registry prefectcontainers --image $IMAGE_NAME --file flows/sandbox-azure/Dockerfile .
echo "Creating new container called ${CONTAINER_NAME}..."
az container create \
--resource-group $RESOURCE_GROUP \
--name $CONTAINER_NAME \
--image prefectcontainers.azurecr.io/$IMAGE_NAME \
--registry-login-server prefectcontainers.azurecr.io \
--registry-username prefectcontainers \
--registry-password $REGISTRY_PW \
--secure-environment-variables $ENV_VARS \
--command-line "/bin/bash -c 'prefect agent start -p Prime-Pool -q $WORKER_NAME'"

# Validate container creation
echo "Checking container: $CONTAINER_NAME status..."
az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query "{ProvisioningState:provisioningState, Status:containers[0].instanceView.currentState.state}" --output table