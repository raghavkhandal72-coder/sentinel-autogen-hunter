package com.sentinel.hunter;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

/**
 * Enterprise Java SDK Client for Sentinel-AutoGen-Hunter Threat Orchestration Gateway.
 */
public class SentinelClient {

    private final HttpClient httpClient;
    private final String baseUrl;

    public SentinelClient(String baseUrl) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();
    }

    public SentinelClient() {
        this("http://localhost:8000");
    }

    /**
     * Checks orchestrator health.
     */
    public String checkHealth() throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/health"))
                .GET()
                .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    /**
     * Ingests telemetry event for autonomous multi-agent analysis.
     */
    public String ingestTelemetry(String service, String ip, String rawLog) throws IOException, InterruptedException {
        String jsonPayload = String.format(
                "{\"service\":\"%s\",\"event_type\":\"auth_attempt\",\"source_ip\":\"%s\",\"raw_log\":\"%s\"}",
                service, ip, rawLog.replace("\"", "\\\"")
        );

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/v1/telemetry"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
