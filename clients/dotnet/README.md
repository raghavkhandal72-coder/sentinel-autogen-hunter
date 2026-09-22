# Sentinel.AutoGen.Hunter (.NET Client SDK)

Enterprise C# / .NET SDK Client for Sentinel-AutoGen-Hunter autonomous multi-agent threat hunting, deception grid, and gateway orchestrator.

## Installation

Add the NuGet package from GitHub Packages:

```bash
dotnet add package Sentinel.AutoGen.Hunter --source https://nuget.pkg.github.com/raghavkhandal72-coder/index.json
```

## Quick Start

```csharp
using Sentinel.AutoGen.Hunter;

var client = new SentinelClient("http://localhost:8000");

// Check health
var health = await client.GetHealthAsync();
Console.WriteLine($"Sentinel Health: {health}");

// Ingest telemetry
var response = await client.ScanTelemetryAsync("sshd", "192.168.1.50", "Failed password for root from 192.168.1.50");
Console.WriteLine($"Hunt Analysis: {response}");
```
