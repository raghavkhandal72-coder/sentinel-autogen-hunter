using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace Sentinel.AutoGen.Hunter
{
    /// <summary>
    /// Enterprise .NET SDK Client for Sentinel-AutoGen-Hunter Threat Orchestration Gateway.
    /// </summary>
    public class SentinelClient
    {
        private readonly HttpClient _httpClient;
        private readonly string _endpoint;

        public SentinelClient(string endpoint = "http://localhost:8000", HttpClient? httpClient = null)
        {
            _endpoint = endpoint.TrimEnd('/');
            _httpClient = httpClient ?? new HttpClient();
        }

        /// <summary>
        /// Retrieves health status from the orchestrator engine.
        /// </summary>
        public async Task<string> GetHealthAsync()
        {
            var response = await _httpClient.GetAsync($"{_endpoint}/health");
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadAsStringAsync();
        }

        /// <summary>
        /// Sends telemetry for autonomous multi-agent analysis.
        /// </summary>
        public async Task<string> ScanTelemetryAsync(string service, string ip, string rawLog)
        {
            var json = $"{{\"service\":\"{service}\",\"event_type\":\"auth_attempt\",\"source_ip\":\"{ip}\",\"raw_log\":\"{rawLog}\"}}";
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync($"{_endpoint}/api/v1/telemetry", content);
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadAsStringAsync();
        }

        /// <summary>
        /// Interacts with the Sentinel Gateway OpenClaw-compatible Chat Completions API.
        /// </summary>
        public async Task<string> PromptSwarmAsync(string prompt)
        {
            var json = $"{{\"model\":\"sentinel-autogen-hunter\",\"messages\":[{{\"role\":\"user\",\"content\":\"{prompt}\"}}]}}";
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync($"{_endpoint}/v1/chat/completions", content);
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadAsStringAsync();
        }
    }
}
