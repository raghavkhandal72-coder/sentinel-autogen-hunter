// ==============================================================================
// Microsoft Sentinel & Azure Log Analytics Provisioning Template (Azure Bicep)
// Architecture: Autonomous Cloud Threat Ingestion for Microsoft AutoGen Swarm
// ==============================================================================

@description('Azure geographical region for Sentinel deployment.')
param location string = resourceGroup().location

@description('Name of the Log Analytics Workspace for AI threat telemetry.')
param workspaceName string = 'ThreatHunter-SentinelWorkspace'

@description('Data retention period in days (Standard enterprise tier: 30-90 days).')
param retentionDays int = 30

// 1. Provision Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: workspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: retentionDays
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// 2. Enable Microsoft Sentinel Solution on the Workspace
resource sentinelSolution 'Microsoft.OperationsManagement/solutions@2015-11-01-preview' = {
  name: 'SecurityInsights(${logAnalyticsWorkspace.name})'
  location: location
  properties: {
    workspaceResourceId: logAnalyticsWorkspace.id
  }
  plan: {
    name: 'SecurityInsights(${logAnalyticsWorkspace.name})'
    product: 'OMSGallery/SecurityInsights'
    publisher: 'Microsoft'
    promotionCode: ''
  }
}

// 3. Outputs for AI Orchestrator Environment Configuration
output workspaceId string = logAnalyticsWorkspace.properties.customerId
output workspaceResourceId string = logAnalyticsWorkspace.id
output workspaceName string = logAnalyticsWorkspace.name
