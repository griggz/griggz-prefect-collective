# Prefect Collective

### Core Components:

- **Prefect Cloud**: Serves as the backbone for orchestrating and managing the diverse data pipelines. Its dynamic nature ensures adaptability and resilience in handling a variety of workflows.
- **Azure**: Microsoft's cloud services suite, instrumental in providing infrastructure support, containerization, data storage, and scalability.

### Prefect Cloud

- **Unified Workflow Management** : With Prefect Cloud, every data workflow, irrespective of its source or nature, can be seamlessly integrated, monitored, and managed from a single pane.

- **Dynamic Task and Flow Structures**: From straightforward data extractions to complex analytical processes, Prefect’s task and flow system is versatile enough to handle the gamut of data operations.

- **Monitoring & Alerts**: Prefect Cloud provides real-time monitoring capabilities, ensuring that any anomalies or failures are promptly detected and addressed.

- **Scalability**: As data operations grow, Prefect ensures that scaling, both in terms of data volume and complexity, remains hassle-free.

### Azure Integration

- **Azure Container Instances (ACI)**: Serve as isolated environments for running Prefect flows, ensuring consistency and reliability across runs.

- **Azure Container Registry**: A secure vault for Docker container images, ensuring optimized deployments and secure storage.

- **Azure Storage**: A robust storage solution that can handle the diverse data storage needs of an organization, from raw data to processed insights.


## Getting Started

Setting up a robust infrastructure on Azure is essential for seamless orchestration and management of data pipelines. This section provides a step-by-step guide to initialize the Azure components and integrate them with Prefect Cloud.

### 1. Azure Portal Setup

Before diving into the technical details, ensure you have an active Azure account and access to the Azure Portal.

### 2. Azure Resource Group

Start by creating a Resource Group. It acts as a logical container where Azure resources, like storage accounts and container instances, are deployed.

- Navigate to Resource groups > Add.

- Select your subscription, and provide a unique name and region for your Resource Group.

### 3. Azure Container Registry (ACR)

ACR is the place where your Docker images will be stored securely.

- Navigate to Container registries > Add.
- Provide a unique name, select your subscription, and the Resource Group you created.
- Under Admin user, choose Enable to access the registry with the Azure portal's credentials.

or

- Using the cli with "prefect-agent-image:latest" as an example name: 
```
az acr build --registry [container registry name] --image prefect-agent-image:latest .
```

### 4. Azure Storage Account

This will act as the backbone for storing all the data and artifacts.

- Navigate to Storage accounts > Add.
- Fill in the necessary details, ensuring it's in the same Resource Group.
- Once the storage account is set up, you can create containers (similar to directories) within it for organized storage.



### 5. Azure Container Instances (ACI)

ACI offers fast and isolated Docker containers, perfect for running Prefect flows.

- Navigate to Container instances > Add.
- Choose the image source as Azure Container Registry and select the appropriate image.
- Fill in other details like size, network, etc., ensuring it's within the previously created Resource Group.

or

- Using the cli with:

```
az container create \                                                 
--resource-group prefect-agents \
--name prefect-agent \
--image "azure container image" \
--registry-login-server "" \
--registry-username "" \
--registry-password "" \
--secure-environment-variables PREFECT_API_URL='https://api.prefect.cloud/api/accounts/[account]/workspaces/[workspace id]' PREFECT_API_KEY='' \
--command-line "/bin/bash -c 'prefect agent start -p [worker pool name] -q [worker name]'"
```
### 6. Connecting Azure to Prefect Cloud

Ensure you have the Prefect CLI installed and authenticated with Prefect Cloud. Create a new project, and when deploying your flows, specify the executor to be DockerAgent and provide the Azure Container Registry URL for image storage. Use the prefect.yaml to structure your project and use the following sample command to deploy: 

```
prefect deploy
```

### AUDIENCE NOTE
All of the container management and deployment processes are automated using the `deploy.sh` script. To learn more, read below.

# Flow Container Management and Deployment

This document provides a step-by-step explanation of the standard bash script designed for managing Docker containers within an Azure environment, specifically tailored for deploying a Prefect agent. The script automates the process of building a new Docker image, cleaning up old container instances, and deploying a new container instance with the freshly built image.

## Flow Requirements
Every new module, that is, folder within the `flows/` directory must cointain the following files if it is to be deployed to prefect:

```
- requirements.txt
- .env
- Dockerfile
- deploy.sh
```

## `deploy.sh` Script Overview

The deployment script performs several key operations:

- Prevents Partial Execution: Ensures that if any command fails, the script stops immediately to prevent partial or faulty deployments.

- Sets Variables: Defines variables for later use, including names and configurations for the Docker image and Azure Container Instance (ACI).

- Cleans Up Old Containers: Lists and deletes old container instances based on a naming convention and date.

- Builds Docker Image: Logs into Azure Container Registry (ACR), builds a new Docker image, and pushes it to ACR.

- Deploys New Container: Creates a new ACI using the newly built Docker image.

- Validates Deployment: Checks the status of the newly deployed container.
    
## Detailed Explanation
### Step 1: Ensure Script Stops on First Error

bash

`set -e`

This command configures the script to exit immediately if any command returns a non-zero exit status, which indicates an error. It's a safety feature to avoid executing subsequent commands if something goes wrong.

### Step 2: Define Configuration Variables

Variables like WORKER_NAME, IMAGE_BASE_NAME, and IMAGE_TAG are set for use in naming Docker images and container instances. The IMAGE_TAG is dynamically generated to include the current date and time, ensuring uniqueness for each build. Environment variables (ENV_VARS) are extracted from a .env file, and the Azure Container Registry password (REGISTRY_PW) is retrieved.

### Step 3: Clean Up Old Containers 

The script lists all containers in the specified Azure resource group and deletes those matching a specific naming pattern (defined by regex), which includes the container prefix followed by a datetime stamp. This step ensures that outdated container instances are removed before deploying a new version.

### Step 4: Build and Push Docker Image

The script logs into ACR (az acr login) and uses az acr build to build a new Docker image from a Dockerfile located in the flows/finance directory. The image is tagged with the unique IMAGE_TAG and pushed to the registry.

### Step 5: Deploy New Container Instance

Using az container create, the script deploys a new container instance to Azure Container Instances. It specifies the container's name, image source, registry information, and the command to start the Prefect agent, along with any required environment variables.

### Step 6: Validate Container Creation

Finally, the script checks the provisioning and current state of the newly created container to ensure it was successfully deployed and is in the expected state.

### Audience Note

For those familiar with Docker, Azure, or Prefect, many of these steps will be recognizable as common tasks associated with container management and deployment. However, even without deep technical knowledge in these areas, this readme aims to demystify the script's operations and provide insight into its automated workflow for deploying and managing containerized applications efficiently.
