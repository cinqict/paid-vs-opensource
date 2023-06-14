variable "databricks_connection_profile" {}

terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
    }
    databricks = {
      source = "databricks/databricks"
    }
  }
}

provider "azurerm" {
  features {}
}

# Use Databricks CLI authentication.
provider "databricks" {
  profile = var.databricks_connection_profile
}