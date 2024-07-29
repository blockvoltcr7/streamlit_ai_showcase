# Configure the Azure provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.65"
    }
  }

  required_version = ">= 0.14.9"
}

provider "azurerm" {
  features {}
}

# Create a resource group
resource "azurerm_resource_group" "rg" {
  name     = "dev_env_learning"
  location = "eastus"
}

# Create a storage account
resource "azurerm_storage_account" "storage" {
  name                     = "devenvstreamlitappsai"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  tags = {
    environment = "dev"
  }
}

# Create a container in the storage account
resource "azurerm_storage_container" "container" {
  name                  = "mycontainer"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

# Output the storage account name
output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}

# Output the primary blob endpoint
output "primary_blob_endpoint" {
  value = azurerm_storage_account.storage.primary_blob_endpoint
}