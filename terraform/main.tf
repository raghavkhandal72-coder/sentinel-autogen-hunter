# ==============================================================================
# Sample Cloud Infrastructure Terraform Manifest
# Demonstrates both hardened resources and intentional security policy triggers
# for Sentinel-AutoGen-Hunter's Shift-Left IaC Scanner.
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Compliant: Hardened Resource Group
resource "azurerm_resource_group" "secops_rg" {
  name     = "rg-sentinel-threat-hunter"
  location = "eastus"
  tags = {
    Environment = "Production"
    ManagedBy   = "Sentinel-AutoGen-Hunter"
  }
}

# Compliant: Hardened Azure Storage Account (Encrypted, Private)
resource "azurerm_storage_account" "secure_storage" {
  name                     = "stautogenthreatlogs"
  resource_group_name      = azurerm_resource_group.secops_rg.name
  location                 = azurerm_resource_group.secops_rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  # Zero-Trust controls
  public_network_access_enabled = false
  min_tls_version               = "TLS1_2"
  enable_https_traffic_only     = true
}

# Hardened Network Security Group
resource "azurerm_network_security_group" "hardened_nsg" {
  name                = "nsg-orchestrator-control"
  location            = azurerm_resource_group.secops_rg.location
  resource_group_name = azurerm_resource_group.secops_rg.name

  # Strictly bounded inbound management
  security_rule {
    name                       = "AllowBastionSSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "10.100.4.0/24" # Bounded corporate VPN CIDR
    destination_address_prefix = "*"
  }
}
