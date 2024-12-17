#!/bin/bash

###########################################
# Prefect Azure Container Instance (ACI) Worker Pool Setup Script
###########################################
# Based on: https://docs.prefect.io/integrations/prefect-azure/aci_worker
#
# Description:
#   This script automates the setup of a Prefect workpool using Azure Container Instances (ACI).
#   If the workpool already exists, it will skip the infrastructure creation and exit.
#   Otherwise, it checks for the existence of all necessary Azure resources and creates them if they don't exist.
#   It then configures the workpool in the Prefect UI.
#   - Resource Group
#   - Azure Container Registry (ACR)
#   - Managed Identity
#   - Custom Role Definitions
#   - Role Assignments
#   - Container Instance
#
# Prerequisites:
#   - Azure CLI installed and logged in
#   - Docker installed
#   - Python with pip installed
#   - Local .env file containing Prefect Cloud credentials:
#     - PREFECT_API_KEY # This is the API key
#     - PREFECT_ACCOUNT_ID # This is the account ID, not the account name
#     - PREFECT_WORKSPACE_ID # This is the workspace ID, not the workspace name
#
# Required Configuration:
#   The following variables must be set before running this script:
#   - LOCATION: Azure region (e.g., "eastus")
#   - WORK_POOL_NAME: Name for your work pool
#   - REGISTRY_NAME: Name for Azure Container Registry
#   - RG_NAME: Azure Resource Group name
#   - PREFECT_WORKSPACE: Prefect Cloud workspace name
#
# Usage:
#   1. Set the required configuration variables
#   2. Ensure .env file exists with required credentials
#   3. Run: bash create_aci_pool.sh
#
# Note:
#   After successful execution, manual configuration in the Prefect UI
#   is required to complete the work pool setup.
###########################################

set -e

# Load environment variables
source .env

###################
# Global Variables
###################

# Azure Configuration
# THE FOLLOWING 5 VARIABLES MUST BE SET PRIOR TO RUNNING THIS SCRIPT
LOCATION="eastus"
WORK_POOL_NAME="aci-pool"
REGISTRY_NAME="prefectaciregistry"
RG_NAME="pre-sales-se"
PREFECT_WORKSPACE="se-demos"

# Derived Variables
IDENTITY_NAME="${WORK_POOL_NAME}-identity"

# Required Environment Variables (from .env)
required_env_vars=(
    "PREFECT_API_KEY"
    "PREFECT_ACCOUNT_ID"
    "PREFECT_WORKSPACE_ID"
)

# Load environment variables from local .env if it exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -E "^PREFECT_API_URL|^PREFECT_API_KEY|^PREFECT_WORKSPACE|^PREFECT_ACCOUNT_ID|^PREFECT_WORKSPACE_ID" | xargs)
else
    echo "Error: .env file not found"
    echo "Please create a .env file with PREFECT_API_URL, PREFECT_API_KEY, and PREFECT_WORKSPACE"
    exit 1
fi

# Check if required environment variables exist and are not empty
if [ -z "$PREFECT_WORKSPACE" ] || [ -z "$PREFECT_ACCOUNT_ID" ] || [ -z "$PREFECT_WORKSPACE_ID" ]; then
    echo "Error: Required environment variables are missing"
    echo "PREFECT_WORKSPACE: ${PREFECT_WORKSPACE:-'not set'}"
    echo "PREFECT_ACCOUNT_ID: ${PREFECT_ACCOUNT_ID:-'not set'}"
    echo "PREFECT_WORKSPACE_ID: ${PREFECT_WORKSPACE_ID:-'not set'}"
    exit 1
fi

# Set PREFECT_API_URL if empty or doesn't exist
if [ -z "${PREFECT_API_URL}" ]; then
    echo "Setting PREFECT_API_URL..."
    export PREFECT_API_URL="https://api.prefect.cloud/api/accounts/${PREFECT_ACCOUNT_ID}/workspaces/${PREFECT_WORKSPACE_ID}"
    echo "PREFECT_API_URL set to: $PREFECT_API_URL"
fi

# Container Configuration
CONTAINER_IMAGE="docker.io/prefecthq/prefect:3-python3.12"
CONTAINER_COMMAND="/bin/bash -c 'pip install prefect-azure && prefect worker start --pool ${WORK_POOL_NAME} --type azure-container-instance'"

# Role Definition
CUSTOM_ROLE_DEF='{
    "Name": "Container Instances Contributor",
    "IsCustom": true,
    "Description": "Can create, delete, and monitor container instances.",
    "Actions": [
        "Microsoft.ManagedIdentity/userAssignedIdentities/assign/action",
        "Microsoft.Resources/deployments/*",
        "Microsoft.ContainerInstance/containerGroups/*"
    ],
    "NotActions": [],
    "AssignableScopes": [SCOPE_PLACEHOLDER]
}'

check_workpool() {
    echo "Checking if work pool exists..."
    
    # Check if prefect CLI is installed
    if ! pip list 2>/dev/null | grep -q "prefect" 2>/dev/null; then
        echo "Error: Prefect CLI is not installed."
        echo "Installing Prefect CLI..."
        pip install --quiet prefect
    fi

    # Try to check work pool existence, continue on error
    if prefect work-pool ls 2>/dev/null | grep -q "^${WORK_POOL_NAME}" 2>/dev/null; then
        echo "Work pool ${WORK_POOL_NAME} already exists."
        echo "Skipping infrastructure creation to avoid conflicts."
        exit 0
    else
        echo "Work pool ${WORK_POOL_NAME} not found or could not be checked."
        echo "Proceeding with infrastructure setup..."
    fi
}

# Update check_prerequisites to include prefect-azure
check_prerequisites() {
    echo "Checking prerequisites..."
    
    # Verify required environment variables
    for var in "${required_env_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo "Error: Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Check Azure CLI with detailed instructions
    if ! command -v az &> /dev/null; then
        echo "Error: Azure CLI is not installed."
        echo
        echo "Please install Azure CLI using one of the following methods:"
        echo
        echo "For macOS (using Homebrew):"
        echo "    brew update && brew install azure-cli"
        echo
        echo "For Ubuntu/Debian:"
        echo "    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
        echo
        echo "For Windows:"
        echo "    winget install -e --id Microsoft.AzureCLI"
        echo
        echo "After installation, verify by running:"
        echo "    az --version"
        echo
        echo "Then login to Azure:"
        echo "    az login"
        echo
        echo "For more information, visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi

    # Check Azure login status
    if ! az account show &> /dev/null; then
        echo "Error: Not logged into Azure."
        echo
        echo "Please login to Azure by running:"
        echo "    az login"
        echo
        echo "This will open your default browser to complete authentication."
        exit 1
    fi

    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker is not installed."
        echo
        echo "Please install Docker from:"
        echo "    https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Check prefect-azure installation
    if ! pip list 2>/dev/null | grep -q "prefect-azure" 2>/dev/null; then
        echo "Installing prefect-azure..."
        pip install --quiet prefect-azure
    fi
}

create_resource_group() {
    echo "Checking resource group..."
    
    if az group show --name $RG_NAME &>/dev/null; then
        echo "Resource group $RG_NAME already exists"
    else
        echo "Creating resource group $RG_NAME..."
        az group create --name $RG_NAME --location $LOCATION
    fi
    
    # Save resource group scope
    export RG_SCOPE=$(az group show --name $RG_NAME --query id --output tsv)
    echo "Resource group scope: $RG_SCOPE"
}

setup_permissions() {
    echo "Checking ACI permissions..."
    
    # Check if custom role exists
    if az role definition list --name "Container Instances Contributor" &>/dev/null; then
        echo "Custom role 'Container Instances Contributor' already exists"
    else
        echo "Creating custom role..."
        local role_def=${CUSTOM_ROLE_DEF/SCOPE_PLACEHOLDER/\"$RG_SCOPE\"}
        az role definition create --role-definition "$role_def"
    fi

    # Check if identity exists
    if az identity show --name $IDENTITY_NAME --resource-group $RG_NAME &>/dev/null; then
        echo "Managed identity $IDENTITY_NAME already exists"
    else
        echo "Creating managed identity..."
        az identity create -g $RG_NAME -n $IDENTITY_NAME
        echo "Waiting for managed identity to propagate..."
        sleep 30  # Wait for 30 seconds for the identity to propagate
    fi

    # Get identity IDs with retry
    MAX_RETRIES=5
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if IDENTITY_PRINCIPAL_ID=$(az identity show --name $IDENTITY_NAME --resource-group $RG_NAME --query principalId --output tsv 2>/dev/null); then
            export IDENTITY_PRINCIPAL_ID
            export IDENTITY_ID=$(az identity show --name $IDENTITY_NAME --resource-group $RG_NAME --query id --output tsv)
            break
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
                echo "Error: Failed to get identity information after $MAX_RETRIES attempts"
                exit 1
            fi
            echo "Waiting for identity to be available... (Attempt $RETRY_COUNT of $MAX_RETRIES)"
            sleep 10
        fi
    done

    # Check role assignments with retry
    echo "Checking role assignments..."
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if ! az role assignment list --assignee $IDENTITY_PRINCIPAL_ID --role "Container Instances Contributor" --scope $RG_SCOPE &>/dev/null; then
            echo "Assigning Container Instances Contributor role..."
            if az role assignment create \
                --assignee $IDENTITY_PRINCIPAL_ID \
                --role "Container Instances Contributor" \
                --scope $RG_SCOPE; then
                break
            fi
        else
            echo "Role 'Container Instances Contributor' already assigned"
            break
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            echo "Error: Failed to assign Container Instances Contributor role after $MAX_RETRIES attempts"
            exit 1
        fi
        echo "Waiting for identity to be available for role assignment... (Attempt $RETRY_COUNT of $MAX_RETRIES)"
        sleep 10
    done

    # Similar retry for AcrPull role
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if ! az role assignment list --assignee $IDENTITY_PRINCIPAL_ID --role "AcrPull" --scope $RG_SCOPE &>/dev/null; then
            echo "Assigning AcrPull role..."
            if az role assignment create \
                --assignee $IDENTITY_PRINCIPAL_ID \
                --role "AcrPull" \
                --scope $RG_SCOPE; then
                break
            fi
        else
            echo "Role 'AcrPull' already assigned"
            break
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            echo "Error: Failed to assign AcrPull role after $MAX_RETRIES attempts"
            exit 1
        fi
        echo "Waiting for identity to be available for role assignment... (Attempt $RETRY_COUNT of $MAX_RETRIES)"
        sleep 10
    done
}

create_acr_registry() {
    echo "Checking Azure Container Registry..."
    
    if az acr show --name $REGISTRY_NAME --resource-group $RG_NAME &>/dev/null; then
        echo "Container registry $REGISTRY_NAME already exists"
    else
        echo "Creating Azure Container Registry..."
        az acr create --resource-group $RG_NAME \
            --name $REGISTRY_NAME --sku Basic
    fi

    # Enable admin access if not already enabled
    echo "Enabling admin access on ACR..."
    az acr update -n $REGISTRY_NAME --admin-enabled true

    # Get ACR credentials
    echo "Getting ACR credentials..."
    ACR_USERNAME=$(az acr credential show -n $REGISTRY_NAME --query "username" -o tsv)
    ACR_PASSWORD=$(az acr credential show -n $REGISTRY_NAME --query "passwords[0].value" -o tsv)

    # Check if Prefect image exists in ACR
    echo "Checking if Prefect image exists in ACR..."
    if ! az acr repository show --name $REGISTRY_NAME --image "prefecthq/prefect:3-python3.12" &>/dev/null; then
        echo "Importing Prefect image from Docker Hub to ACR..."
        az acr import \
            --name $REGISTRY_NAME \
            --source docker.io/prefecthq/prefect:3-python3.12 \
            --image prefecthq/prefect:3-python3.12
    else
        echo "Prefect image already exists in ACR"
    fi
}

create_worker_container() {
    echo "Checking worker container instance..."
    
    if az container show --name $WORK_POOL_NAME --resource-group $RG_NAME &>/dev/null; then
        echo "Container instance $WORK_POOL_NAME already exists"
    else
        # Get ACR credentials
        echo "Getting ACR credentials..."
        ACR_USERNAME=$(az acr credential show -n $REGISTRY_NAME --query "username" -o tsv)
        ACR_PASSWORD=$(az acr credential show -n $REGISTRY_NAME --query "passwords[0].value" -o tsv)

        echo "Creating worker container instance..."
        az container create \
            --name $WORK_POOL_NAME \
            --resource-group $RG_NAME \
            --assign-identity $IDENTITY_ID \
            --image "$REGISTRY_NAME.azurecr.io/prefecthq/prefect:3-python3.12" \
            --registry-login-server "$REGISTRY_NAME.azurecr.io" \
            --registry-username "$ACR_USERNAME" \
            --registry-password "$ACR_PASSWORD" \
            --os-type Linux \
            --cpu 1 \
            --memory 1.5 \
            --secure-environment-variables \
                PREFECT_API_URL=$PREFECT_API_URL \
                PREFECT_API_KEY=$PREFECT_API_KEY \
            --command-line "$CONTAINER_COMMAND"
    fi
}


update_work_pool_config() {
    echo "Updating work pool configuration..."
    echo "Please manually update the following configurations in your Prefect UI work pool settings:"
    echo
    echo "Identities:"
    echo "[$IDENTITY_ID]"
    echo
    echo "ACRManagedIdentity:"
    echo "Identity: $IDENTITY_ID"
    echo "Registry URL: $REGISTRY_NAME.azurecr.io"
    echo
    echo "Subscription ID and Resource Group:"
    echo "These can be found in: $RG_SCOPE"
}

# Update main function to include workpool check
main() {
    echo "Starting ACI worker deployment..."
    
    check_prerequisites
    check_workpool
    create_resource_group
    setup_permissions
    create_acr_registry
    create_worker_container
    update_work_pool_config
    
    echo "ACI worker deployment complete!"
    echo "Please complete the manual configuration steps in the Prefect UI as described above."
}

main
