resource "azurerm_resource_group" "lisan-algaib" {
  name     = "algaib"
  location = var.resource_group_location
}

resource "azurerm_storage_account" "adls" {
  name                     = "benegesserit"
  resource_group_name      = azurerm_resource_group.lisan-algaib.name
  location                 = azurerm_resource_group.lisan-algaib.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "blob" {
  name                  = "atreides"
  storage_account_name  = azurerm_storage_account.adls.name
  container_access_type = "private"
}

resource "azurerm_mssql_server" "sql_server" {
  name                         = "arrakis-sql-server"
  resource_group_name          = azurerm_resource_group.lisan-algaib.name
  location                     = azurerm_resource_group.lisan-algaib.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_username
  administrator_login_password = var.sql_admin_password
}

resource "azurerm_mssql_database" "database" {
  name           = "spice-db"
  server_id      = azurerm_mssql_server.sql_server.id
  sku_name       = "Basic"
  zone_redundant = false
  max_size_gb    = 2
}

resource "azurerm_mssql_firewall_rule" "allow_azure_services" {
  name             = "fremen"
  server_id        = azurerm_mssql_server.sql_server.id
  start_ip_address = var.start_client_ip_address
  end_ip_address   = var.end_client_ip_address
}

# Create an Azure AD application
resource "azuread_application" "spice_app" {
  display_name = "spice-harvester-app"
}

# Create a service principal associated with the application
resource "azuread_service_principal" "spice_sp" {
  client_id = azuread_application.spice_app.client_id
}

# Create a password for the service principal
resource "azuread_service_principal_password" "spice_sp_password" {
  service_principal_id = azuread_service_principal.spice_sp.id
  end_date             = "2025-06-01T00:00:00Z"
}

# Assign Storage Blob Data Contributor role to the service principal for the container
resource "azurerm_role_assignment" "sp_storage_role" {
  scope                = azurerm_storage_container.blob.resource_manager_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azuread_service_principal.spice_sp.id
}

# Output the service principal credentials for later use
output "service_principal_application_id" {
  value     = azuread_application.spice_app.client_id
  sensitive = true
}

output "service_principal_password" {
  value     = azuread_service_principal_password.spice_sp_password.value
  sensitive = true
}