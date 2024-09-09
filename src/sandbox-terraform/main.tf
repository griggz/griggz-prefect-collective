provider "azurerm" {
  features = {}
}

resource "azurerm_resource_group" "rg" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_storage_account" "storage" {
  name                     = "examplestorage"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "container" {
  name                  = "codecontainer"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

resource "azurerm_container_registry" "acr" {
  name                = "exampleacr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_container_group" "prefect_worker" {
  name                = "prefect-worker-group"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"

  container {
    name   = "prefect-worker"
    image  = "${azurerm_container_registry.acr.login_server}/prefect-worker:latest"
    cpu    = "0.5"
    memory = "1.5"

    environment_variables = {
      PREFECT_API_URL = "https://api.prefect.io"
      PREFECT_AGENT_NAME = "example-agent"
    }
  }

  image_registry_credential {
    server   = azurerm_container_registry.acr.login_server
    username = azurerm_container_registry.acr.admin_username
    password = azurerm_container_registry.acr.admin_password
  }
}
