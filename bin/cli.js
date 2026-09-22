#!/usr/bin/env node

/**
 * Sentinel-AutoGen-Hunter CLI for Node.js / npx
 * Architect: Raghav Khandal (@raghavkhandal72-coder)
 */

const { SentinelClient } = require('../index.js');

const args = process.argv.slice(2);
const command = args[0] || 'status';

console.log('\x1b[36m%s\x1b[0m', '================================================================================');
console.log('\x1b[1m\x1b[32m%s\x1b[0m', '🛡️  Sentinel-AutoGen-Hunter (OpenClaw Multi-Channel Gateway Node.js CLI)');
console.log('\x1b[36m%s\x1b[0m', '    Architect: Raghav Khandal (@raghavkhandal72-coder) | Version: 1.4.1');
console.log('\x1b[36m%s\x1b[0m', '================================================================================\n');

const client = new SentinelClient();

async function run() {
  try {
    if (command === 'status') {
      console.log('\x1b[33m[*] Probing local Gateway on http://localhost:8000...\x1b[0m');
      const status = await client.getGatewayStatus();
      console.log('\x1b[32m✔ Gateway Online!\x1b[0m');
      console.log('Status:            ', status.status);
      console.log('Version:           ', status.version);
      console.log('Defense Shield:    ', status.defense_shield);
      console.log('Supported Channels:', (status.supported_channels || []).join(', '));
      console.log('Paired Devices:    ', (status.paired_devices || []).join(', '));
    } else if (command === 'chat') {
      const message = args.slice(1).join(' ') || 'Report threat swarm telemetry';
      console.log(`[USER -> OPENCLAW (Node.js)]: ${message}`);
      const res = await client.sendMessage('companion', 'node_cli_user', message);
      console.log(`[STATUS]: ${res.status}`);
      console.log(`[OPENCLAW RESPONSE]: ${res.response}\n`);
    } else if (command === 'mitre') {
      console.log('\x1b[33m[*] Fetching MITRE ATT&CK Enterprise Matrix...\x1b[0m');
      const mitre = await client.getMitreCoverage();
      console.log(`Overall MITRE Coverage: ${mitre.overall_coverage_pct}%`);
      console.log(`Covered Techniques: ${mitre.covered_techniques}/${mitre.total_techniques_in_scope}`);
    } else {
      console.log('Available Commands:');
      console.log('  npx @raghavkhandal72-coder/sentinel-autogen-hunter status');
      console.log('  npx @raghavkhandal72-coder/sentinel-autogen-hunter chat "Your prompt"');
      console.log('  npx @raghavkhandal72-coder/sentinel-autogen-hunter mitre');
    }
  } catch (err) {
    console.error('\x1b[31m%s\x1b[0m', `[!] Error communicating with Gateway: ${err.message}`);
    console.log('\x1b[33m💡 Tip: Start the local Sentinel gateway first:\x1b[0m');
    console.log('   python -m cli.main openclaw-gateway --port 8000');
    console.log('   or launch the companion: python companion.py\n');
  }
}

run();
