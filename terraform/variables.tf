variable "start_client_ip_address" {
  description = "Your start IP address for SQL Server firewall rules"
  type        = string
  sensitive   = true
  default     = "0.0.0.0"
}

variable "end_client_ip_address" {
  description = "Your end IP address for SQL Server firewall rules"
  type        = string
  sensitive   = true
  default     = "0.0.0.0"
}

variable "sql_admin_username" {
  description = "The administrator username for the SQL Server"
  type        = string
  sensitive   = true
  default     = "gomjobbar"
}

variable "sql_admin_password" {
  description = "The administrator password for the SQL Server"
  type        = string
  sensitive   = true
  default     = "Foobar@123"
}

variable "resource_group_location" {
  description = "The location for the resource group"
  type        = string
  default     = "UK South"
}