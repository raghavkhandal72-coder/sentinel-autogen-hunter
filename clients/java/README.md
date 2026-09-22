# Sentinel-AutoGen-Hunter Java SDK

Enterprise Java SDK Client for Sentinel-AutoGen-Hunter autonomous multi-agent threat hunting, deception grid, and gateway orchestrator.

## Installation

Add the dependency from GitHub Packages in your `pom.xml`:

```xml
<dependency>
  <groupId>com.sentinel.hunter</groupId>
  <artifactId>sentinel-autogen-hunter</artifactId>
  <version>1.4.1</version>
</dependency>
```

Add GitHub Packages repository in `pom.xml` or `settings.xml`:

```xml
<repositories>
  <repository>
    <id>github</id>
    <url>https://maven.pkg.github.com/raghavkhandal72-coder/sentinel-autogen-hunter</url>
  </repository>
</repositories>
```

## Quick Start

```java
import com.sentinel.hunter.SentinelClient;

public class App {
    public static void main(String[] args) throws Exception {
        SentinelClient client = new SentinelClient("http://localhost:8000");
        String health = client.checkHealth();
        System.out.println("Sentinel Health: " + health);
    }
}
```
