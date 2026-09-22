/**
 * Sentinel-AutoGen-Hunter & OpenClaw Gateway Node.js Client SDK
 * Architect: Raghav Khandal (@raghavkhandal72-coder)
 * License: MIT
 */

const http = require('http');
const https = require('https');
const { URL } = require('url');

class SentinelClient {
  constructor(options = {}) {
    this.baseUrl = options.baseUrl || process.env.SENTINEL_GATEWAY_URL || 'http://localhost:8000';
  }

  async _request(method, path, data = null) {
    const targetUrl = new URL(path, this.baseUrl);
    const client = targetUrl.protocol === 'https:' ? https : http;

    return new Promise((resolve, reject) => {
      const payload = data ? JSON.stringify(data) : null;
      const headers = {
        'Accept': 'application/json',
        'User-Agent': 'Sentinel-NodeJS-Client/1.4.1'
      };

      if (payload) {
        headers['Content-Type'] = 'application/json';
        headers['Content-Length'] = Buffer.byteLength(payload);
      }

      const req = client.request(targetUrl, { method, headers }, (res) => {
        let body = '';
        res.on('data', (chunk) => body += chunk);
        res.on('end', () => {
          try {
            const parsed = JSON.parse(body);
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(parsed);
            } else {
              reject(new Error(`API Error (${res.statusCode}): ${JSON.stringify(parsed)}`));
            }
          } catch (e) {
            resolve(body);
          }
        });
      });

      req.on('error', (err) => reject(err));
      if (payload) req.write(payload);
      req.end();
    });
  }

  async health() {
    return this._request('GET', '/health');
  }

  async getGatewayStatus() {
    return this._request('GET', '/v1/gateway/status');
  }

  async chat(messages, temperature = 0.7) {
    return this._request('POST', '/v1/chat/completions', { messages, temperature });
  }

  async sendMessage(channel, senderId, content) {
    return this._request('POST', '/v1/channels/message', {
      channel,
      sender_id: senderId,
      content
    });
  }

  async executeTool(toolName, toolArgs, callerId = 'nodejs_client') {
    return this._request('POST', '/v1/tools/execute', {
      tool_name: toolName,
      tool_args: toolArgs,
      caller_id: callerId
    });
  }

  async getSandboxPermissions() {
    return this._request('GET', '/v1/sandbox/permissions');
  }

  async pairCompanion(setupCode, clientName = 'NodeJS SDK Client') {
    return this._request('POST', '/v1/gateway/pair', {
      setup_code: setupCode,
      client_name: clientName
    });
  }

  async getMitreCoverage() {
    return this._request('GET', '/mitre/coverage');
  }
}

module.exports = {
  SentinelClient,
  version: '1.4.1'
};
