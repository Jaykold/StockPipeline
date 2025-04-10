terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
  }
}

provider "azurerm" {
  features {}

  # No credentials needed here - Azure CLI handles authentication
}
provider "azuread" {
  # No credentials needed here - Azure CLI handles authentication
}
# The Azure CLI will automatically authenticate using the credentials of the currently logged-in user.