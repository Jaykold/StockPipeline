output "ACC_NAME" {
  value = azurerm_storage_account.adls.name
  description = "The name of the Storage Account"
}

output "CONTAINER_NAME" {
  value = azurerm_storage_container.blob.name
  description = "The name of the storage container"
}

output "ACC_KEY" {
  value = azurerm_storage_account.adls.primary_access_key
  sensitive = true
  description = "The primary access key for the storage account"
}

output "SP_APP_ID" {
  value = azuread_application.spice_app.client_id
  description = "The Application ID of the Service Principal"
}

output "SP_TENANT_ID" {
  value = azuread_service_principal.spice_sp.application_tenant_id
  description = "The Tenant ID of the Azure Active Directory"
}

output "SP_SECRET_ID" {
  value = azuread_application_password.spice_app_password.value
  sensitive = true
  description = "The secret of the application (Storage Account)"
}

output "SQL_SERVER" {
  value = azurerm_mssql_server.sql_server.fully_qualified_domain_name
  description = "The fully qualified domain name of the SQL Server"
}

output "SQL_DB" {
  value = azurerm_mssql_database.database.name
  description = "The name of the SQL Database"
}

output "SQL_USER" {
  value = var.sql_admin_username
  sensitive = true
  description = "The SQL Server admin username"
}

output "SQL_PASSWORD" {
  value = var.sql_admin_password
  sensitive = true
  description = "The SQL Server admin password"
}