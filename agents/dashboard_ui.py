"""HTML5 / Cyberpunk Dark-Mode Web SOC Operations Dashboard for Sentinel-AutoGen-Hunter.

Provides a unified visual control plane for:
- Live Threat Telemetry & Multi-Agent Swarm metrics
- Interactive MITRE ATT&CK Heatmap
- Universal Multi-SIEM Sigma Transpiler Playground
- Canary Honeytoken & Active Deception Studio
- Human-in-the-Loop (HITL) Containment Approvals
- Real-time Attack Simulator
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Sentinel-AutoGen-Hunter | Cyber SOC Command Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700;800&family=Orbitron:wght@600;800;900&display=swap');
        body {
            font-family: 'JetBrains Mono', monospace;
            background-color: #080c14;
            color: #d1d5db;
        }
        .orbitron { font-family: 'Orbitron', sans-serif; }
        .cyber-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(10, 15, 26, 0.95) 100%);
            border: 1px solid rgba(0, 255, 136, 0.18);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(12px);
        }
        .cyber-card:hover {
            border-color: rgba(0, 216, 255, 0.4);
            box-shadow: 0 0 15px rgba(0, 216, 255, 0.15);
        }
        .glow-emerald { text-shadow: 0 0 10px rgba(0, 255, 136, 0.6); }
        .glow-cyan { text-shadow: 0 0 10px rgba(0, 216, 255, 0.6); }
        .glow-crimson { text-shadow: 0 0 10px rgba(255, 51, 102, 0.6); }
        pre, code { font-family: 'JetBrains Mono', monospace; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #080c14; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #00ff88; }
    </style>
</head>
<body class="min-h-screen flex flex-col p-4 md:p-8">

    <!-- Top Navigation Bar -->
    <header class="flex flex-col md:flex-row items-center justify-between pb-6 mb-8 border-b border-emerald-500/20 gap-4">
        <div class="flex items-center space-x-4">
            <div class="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-400/40 flex items-center justify-center text-emerald-400 text-2xl shadow-[0_0_15px_rgba(0,255,136,0.3)]">
                🛡️
            </div>
            <div>
                <h1 class="text-2xl md:text-3xl font-black orbitron tracking-wider text-white">
                    SENTINEL-<span class="text-emerald-400">AUTOGEN</span>-HUNTER
                </h1>
                <p class="text-xs text-gray-400 flex items-center gap-2">
                    <span class="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                    <span class="text-emerald-400 font-semibold">ONLINE</span> • Autonomous Cloud-Native Threat Orchestrator • MCP + Sentinel + Multi-SIEM
                </p>
            </div>
        </div>
        <div class="flex items-center gap-3">
            <span class="px-3 py-1 rounded bg-slate-800/80 border border-slate-700 text-xs text-cyan-400 font-mono">
                <i class="fa-solid fa-microchip mr-1"></i> Multi-Agent Swarm: <span id="agent-count" class="text-white font-bold">4 Active</span>
            </span>
            <span class="px-3 py-1 rounded bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400 font-mono">
                <i class="fa-solid fa-shield-halved mr-1"></i> Zero-Trust: <span class="font-bold">ACTIVE</span>
            </span>
            <a href="/install" class="px-3 py-1.5 rounded bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-xs text-emerald-400 font-bold transition flex items-center gap-1.5">
                <i class="fa-solid fa-download"></i> Install Hub
            </a>
            <a href="https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter" target="_blank" class="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 border border-slate-600 text-xs text-white transition flex items-center gap-2">
                <i class="fa-brands fa-github"></i> Star on GitHub
            </a>
        </div>
    </header>

    <!-- Top KPI Metric Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <div class="cyber-card p-5 rounded-xl">
            <div class="flex justify-between items-start mb-2">
                <span class="text-xs text-gray-400 uppercase tracking-wider font-semibold">Threats Intercepted</span>
                <i class="fa-solid fa-skull-crossbones text-crimson-400 text-rose-500 text-lg"></i>
            </div>
            <div class="text-3xl font-bold orbitron text-white glow-crimson" id="kpi-threats">24</div>
            <p class="text-xs text-gray-500 mt-2"><span class="text-emerald-400">+5</span> in last hour (DFA Pre-filtered)</p>
        </div>
        <div class="cyber-card p-5 rounded-xl">
            <div class="flex justify-between items-start mb-2">
                <span class="text-xs text-gray-400 uppercase tracking-wider font-semibold">Firewall Drop Rules</span>
                <i class="fa-solid fa-lock text-cyan-400 text-lg"></i>
            </div>
            <div class="text-3xl font-bold orbitron text-white glow-cyan" id="kpi-drops">18</div>
            <p class="text-xs text-gray-500 mt-2">DOCKER-USER bridge chain</p>
        </div>
        <div class="cyber-card p-5 rounded-xl">
            <div class="flex justify-between items-start mb-2">
                <span class="text-xs text-gray-400 uppercase tracking-wider font-semibold">Armed Honeytokens</span>
                <i class="fa-solid fa-cube text-amber-400 text-lg"></i>
            </div>
            <div class="text-3xl font-bold orbitron text-amber-400" id="kpi-tokens">6</div>
            <p class="text-xs text-gray-500 mt-2">Canary AWS, GitHub & DB tripwires</p>
        </div>
        <div class="cyber-card p-5 rounded-xl">
            <div class="flex justify-between items-start mb-2">
                <span class="text-xs text-gray-400 uppercase tracking-wider font-semibold">Swarm AI Confidence</span>
                <i class="fa-solid fa-brain text-emerald-400 text-lg"></i>
            </div>
            <div class="text-3xl font-bold orbitron text-emerald-400 glow-emerald" id="kpi-confidence">94.8%</div>
            <p class="text-xs text-gray-500 mt-2">Consensus verification score</p>
        </div>
    </div>

    <!-- Main Workspace: Two Columns -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">

        <!-- Left Column: Universal Multi-SIEM Sigma Synthesizer Playground (7 cols) -->
        <div class="lg:col-span-7 flex flex-col space-y-8">
            <div class="cyber-card p-6 rounded-xl flex-1 flex flex-col">
                <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 mb-4 border-b border-slate-700/60 gap-2">
                    <div>
                        <h2 class="text-lg font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-wand-magic-sparkles text-cyan-400"></i>
                            Universal Multi-SIEM Sigma Transpiler
                        </h2>
                        <p class="text-xs text-gray-400">Synthesizes Sigma Standard YAML and transpiles to Sentinel KQL, Splunk SPL & Elastic ES|QL</p>
                    </div>
                    <button onclick="synthesizeRules()" class="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-black font-bold text-xs rounded shadow transition flex items-center gap-2">
                        <i class="fa-solid fa-play"></i> Synthesize Detection
                    </button>
                </div>

                <!-- Input Controls -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4 text-xs">
                    <div>
                        <label class="block text-gray-400 mb-1">Threat Classification</label>
                        <select id="synth-threat-type" class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-emerald-400">
                            <option value="ssh_brute_force">ssh_brute_force (T1110.001)</option>
                            <option value="port_scan">port_scan (T1046)</option>
                            <option value="credential_access">credential_access (T1552)</option>
                            <option value="canary_breach">canary_breach (T1078.004)</option>
                            <option value="lateral_movement">lateral_movement (T1021.004)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-400 mb-1">Attacker IPv4 / CIDR</label>
                        <input id="synth-ip" type="text" value="198.51.100.42" class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white font-mono focus:outline-none focus:border-emerald-400">
                    </div>
                    <div>
                        <label class="block text-gray-400 mb-1">Target Asset Name</label>
                        <input id="synth-asset" type="text" value="prod-k8s-ingress" class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white font-mono focus:outline-none focus:border-emerald-400">
                    </div>
                </div>

                <!-- SIEM Format Tabs -->
                <div class="flex border-b border-slate-700 mb-3 space-x-2 text-xs overflow-x-auto pb-1">
                    <button onclick="switchTab('tab-sigma')" id="btn-tab-sigma" class="px-3 py-1.5 rounded-t font-semibold bg-emerald-500/20 text-emerald-400 border-b-2 border-emerald-400">
                        Sigma Standard (YAML)
                    </button>
                    <button onclick="switchTab('tab-kql')" id="btn-tab-kql" class="px-3 py-1.5 rounded-t text-gray-400 hover:text-white">
                        Microsoft Sentinel (KQL)
                    </button>
                    <button onclick="switchTab('tab-splunk')" id="btn-tab-splunk" class="px-3 py-1.5 rounded-t text-gray-400 hover:text-white">
                        Splunk (SPL)
                    </button>
                    <button onclick="switchTab('tab-elastic')" id="btn-tab-elastic" class="px-3 py-1.5 rounded-t text-gray-400 hover:text-white">
                        Elastic Security (ES|QL)
                    </button>
                    <button onclick="switchTab('tab-aws')" id="btn-tab-aws" class="px-3 py-1.5 rounded-t text-gray-400 hover:text-white">
                        AWS CloudWatch
                    </button>
                </div>

                <!-- Code Container -->
                <div class="relative flex-1 min-h-[220px]">
                    <button onclick="copyCurrentRule()" class="absolute top-2 right-2 px-2.5 py-1 bg-slate-800/90 hover:bg-slate-700 border border-slate-600 rounded text-xs text-gray-300 transition flex items-center gap-1.5 z-10">
                        <i class="fa-regular fa-copy"></i> <span id="copy-text">Copy Rule</span>
                    </button>
                    <div id="tab-sigma" class="siem-pane">
                        <pre class="bg-black/70 border border-slate-800 rounded-lg p-4 text-xs text-emerald-400 overflow-x-auto h-64 font-mono leading-relaxed"><code id="code-sigma">title: Autonomous Hunt: Suspicious Ssh Brute Force Detected
id: e4b2d511-73ad-5011-8a96-cf9b0713437f
status: test
description: Detects automated ssh_brute_force patterns against prod-k8s-ingress.
tags:
    - attack.credential_access
    - attack.t1110.001
logsource:
    category: authentication
    product: linux
    service: sshd
detection:
    selection_ip:
        src_ip: '198.51.100.42'
    condition: selection_ip
level: high</code></pre>
                    </div>
                    <div id="tab-kql" class="siem-pane hidden">
                        <pre class="bg-black/70 border border-slate-800 rounded-lg p-4 text-xs text-cyan-400 overflow-x-auto h-64 font-mono leading-relaxed"><code id="code-kql">// Microsoft Sentinel Analytical Rule
AutoGenThreatHunt_CL
| where TimeGenerated >= ago(24h)
| where ThreatType == "ssh_brute_force" or AttackerIP == "198.51.100.42"
| summarize EventCount = count() by AttackerIP, TargetAsset, ThreatType
| where EventCount >= 3
| project AttackerIP, TargetAsset, ThreatType, EventCount</code></pre>
                    </div>
                    <div id="tab-splunk" class="siem-pane hidden">
                        <pre class="bg-black/70 border border-slate-800 rounded-lg p-4 text-xs text-amber-400 overflow-x-auto h-64 font-mono leading-relaxed"><code id="code-splunk">index=security sourcetype=linux:auth (src_ip="198.51.100.42" OR signature="ssh_brute_force")
| stats count earliest(_time) as first_seen latest(_time) as last_seen by src_ip, dest, user
| where count >= 3
| sort - count</code></pre>
                    </div>
                    <div id="tab-elastic" class="siem-pane hidden">
                        <pre class="bg-black/70 border border-slate-800 rounded-lg p-4 text-xs text-purple-400 overflow-x-auto h-64 font-mono leading-relaxed"><code id="code-elastic">FROM logs-*
| WHERE @timestamp >= NOW() - 1 day
  AND (source.ip == "198.51.100.42" OR event.category == "ssh_brute_force")
| STATS event_count = COUNT(*) BY source.ip, host.name
| WHERE event_count >= 3</code></pre>
                    </div>
                    <div id="tab-aws" class="siem-pane hidden">
                        <pre class="bg-black/70 border border-slate-800 rounded-lg p-4 text-xs text-blue-400 overflow-x-auto h-64 font-mono leading-relaxed"><code id="code-aws">fields @timestamp, @message, srcAddr, dstAddr
| filter srcAddr = '198.51.100.42' or @message like /FAILED LOGIN/
| stats count(*) as attempts by srcAddr, dstAddr
| filter attempts >= 3</code></pre>
                    </div>
                </div>
            </div>

            <!-- MITRE ATT&CK Matrix Navigator -->
            <div class="cyber-card p-6 rounded-xl">
                <div class="flex items-center justify-between pb-3 mb-4 border-b border-slate-700/60">
                    <div>
                        <h2 class="text-base font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-network-wired text-purple-400"></i>
                            MITRE ATT&CK Real-Time Heatmap
                        </h2>
                        <p class="text-xs text-gray-400">Autonomous tactic classification across enterprise kill chain</p>
                    </div>
                    <span class="px-2.5 py-1 rounded bg-purple-500/10 border border-purple-500/30 text-xs text-purple-400 font-mono">
                        v14.1 Enterprise Matrix
                    </span>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                    <div class="p-3 bg-slate-900/80 border border-slate-800 rounded-lg">
                        <div class="text-gray-400 text-[10px] uppercase">Initial Access</div>
                        <div class="text-white font-bold mt-1">T1078 Valid Accounts</div>
                        <div class="mt-2 text-[10px] text-emerald-400 font-mono">12 events logged</div>
                    </div>
                    <div class="p-3 bg-slate-900/80 border border-rose-500/30 bg-rose-500/5 rounded-lg shadow-[0_0_10px_rgba(244,63,94,0.1)]">
                        <div class="text-rose-400 text-[10px] uppercase font-bold">Credential Access</div>
                        <div class="text-rose-300 font-bold mt-1">T1110.001 Brute Force</div>
                        <div class="mt-2 text-[10px] text-rose-400 font-mono">ACTIVE ATTACK DROP</div>
                    </div>
                    <div class="p-3 bg-slate-900/80 border border-amber-500/30 bg-amber-500/5 rounded-lg">
                        <div class="text-amber-400 text-[10px] uppercase font-bold">Defense Evasion</div>
                        <div class="text-amber-300 font-bold mt-1">T1078.004 Cloud Acct</div>
                        <div class="mt-2 text-[10px] text-amber-400 font-mono">Canary Tripwire Armed</div>
                    </div>
                    <div class="p-3 bg-slate-900/80 border border-slate-800 rounded-lg">
                        <div class="text-gray-400 text-[10px] uppercase">Lateral Movement</div>
                        <div class="text-white font-bold mt-1">T1021.004 SSH Remote</div>
                        <div class="mt-2 text-[10px] text-cyan-400 font-mono">0 breaches verified</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Column: Active Deception, HITL Approvals & Live Attack Simulator (5 cols) -->
        <div class="lg:col-span-5 flex flex-col space-y-8">

            <!-- Active Defense & Honeytoken Deception Studio -->
            <div class="cyber-card p-6 rounded-xl">
                <div class="flex items-center justify-between pb-3 mb-4 border-b border-slate-700/60">
                    <div>
                        <h2 class="text-base font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-fingerprint text-amber-400"></i>
                            Canary Honeytoken Deception
                        </h2>
                        <p class="text-xs text-gray-400">High-fidelity decoy credentials with instantaneous DOCKER-USER isolation</p>
                    </div>
                </div>

                <div class="space-y-3 text-xs mb-4">
                    <div class="flex gap-2">
                        <select id="token-type" class="flex-1 bg-slate-900 border border-slate-700 rounded p-2 text-white">
                            <option value="aws_key">AWS IAM Access Key (AKIA...)</option>
                            <option value="github_token">GitHub PAT (ghp_...)</option>
                            <option value="azure_secret">Azure Service Principal Secret</option>
                            <option value="db_connection">PostgreSQL Decoy URI</option>
                        </select>
                        <button onclick="deployHoneytoken()" class="px-3 py-2 bg-amber-500 hover:bg-amber-400 text-black font-bold rounded shadow transition">
                            <i class="fa-solid fa-plus mr-1"></i> Deploy
                        </button>
                    </div>
                </div>

                <!-- Deployed Honeytokens List -->
                <div class="space-y-2 max-h-48 overflow-y-auto pr-1" id="honeytoken-list">
                    <div class="p-2.5 bg-black/60 border border-slate-800 rounded flex items-center justify-between text-xs">
                        <div>
                            <div class="font-mono text-amber-400 text-[11px]">AKIA94B8A2EXAMPLE77</div>
                            <div class="text-gray-400 text-[10px]">Asset: prod-api-cluster • Status: <span class="text-emerald-400 font-bold">ARMED</span></div>
                        </div>
                        <button onclick="triggerBreach('AKIA94B8A2EXAMPLE77')" class="px-2 py-1 bg-rose-500/20 hover:bg-rose-500/40 border border-rose-500/40 text-rose-300 rounded text-[10px] transition">
                            Simulate Trip
                        </button>
                    </div>
                </div>
            </div>

            <!-- Human-in-the-Loop (HITL) Containment Approvals -->
            <div class="cyber-card p-6 rounded-xl">
                <div class="flex items-center justify-between pb-3 mb-4 border-b border-slate-700/60">
                    <div>
                        <h2 class="text-base font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-user-shield text-cyan-400"></i>
                            Human-in-the-Loop (HITL) Gate
                        </h2>
                        <p class="text-xs text-gray-400">Zero-trust quarantine sign-off for critical infrastructure</p>
                    </div>
                    <span id="hitl-count-badge" class="px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-xs text-cyan-400 font-mono">1 Pending</span>
                </div>
                <div class="space-y-2.5 text-xs" id="hitl-container">
                    <div class="p-3 bg-black/60 border border-slate-700 rounded-lg">
                        <div class="flex justify-between items-start mb-1">
                            <span class="font-bold text-white">Action ID: hitl-9b3f4a</span>
                            <span class="text-rose-400 uppercase font-bold text-[10px]">High Risk Asset</span>
                        </div>
                        <p class="text-gray-400 text-[11px] mb-2">Quarantine internal VPN bastion host <code class="text-cyan-300">10.0.4.15</code></p>
                        <div class="flex gap-2">
                            <button onclick="approveHITL('hitl-9b3f4a')" class="flex-1 py-1 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-400 rounded text-center transition">
                                <i class="fa-solid fa-check mr-1"></i> Authorize Isolation
                            </button>
                            <button onclick="rejectHITL('hitl-9b3f4a')" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-gray-300 rounded transition">
                                Dismiss
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Live Autonomous Attack Simulator -->
            <div class="cyber-card p-6 rounded-xl flex-1">
                <div class="flex items-center justify-between pb-3 mb-4 border-b border-slate-700/60">
                    <div>
                        <h2 class="text-base font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-terminal text-emerald-400"></i>
                            Live Attack Simulator & Console
                        </h2>
                        <p class="text-xs text-gray-400">Trigger simulated attack vectors to observe real-time agent consensus</p>
                    </div>
                </div>
                <div class="flex flex-wrap gap-2 mb-3">
                    <button onclick="simulateAttack('ssh_brute_force')" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-emerald-500/40 rounded text-xs text-white transition flex items-center gap-1.5">
                        <i class="fa-solid fa-key text-rose-400"></i> SSH Brute Force
                    </button>
                    <button onclick="simulateAttack('port_scan')" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-cyan-500/40 rounded text-xs text-white transition flex items-center gap-1.5">
                        <i class="fa-solid fa-radar text-cyan-400"></i> Port Scan
                    </button>
                    <button onclick="simulateAttack('canary_breach')" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-amber-500/40 rounded text-xs text-white transition flex items-center gap-1.5">
                        <i class="fa-solid fa-bolt text-amber-400"></i> Canary Breach
                    </button>
                </div>
                <div class="bg-black/80 border border-slate-800 rounded-lg p-3 text-[11px] text-gray-300 font-mono h-40 overflow-y-auto space-y-1" id="live-console">
                    <div class="text-gray-500">[2026-03-21 16:30:01] System initialized. Telemetry stream connected.</div>
                    <div class="text-emerald-400">[2026-03-21 16:30:02] AutoGen Multi-Agent Swarm ready. Consensus threshold = 0.85</div>
                    <div class="text-cyan-400">[2026-03-21 16:30:03] MCP Server listening for tools invocation.</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="mt-auto pt-6 border-t border-slate-800/80 text-center text-xs text-gray-500 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div>
            <span>Sentinel-AutoGen-Hunter v2.0 Enterprise</span> • Open-source Zero-Trust Autonomous SIEM Orchestrator
        </div>
        <div class="flex items-center gap-4">
            <a href="/docs" class="hover:text-emerald-400 transition">FastAPI OpenAPI Docs</a>
            <a href="/metrics" class="hover:text-emerald-400 transition">Prometheus Metrics</a>
            <a href="https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter" target="_blank" class="hover:text-white transition">GitHub Repo</a>
        </div>
    </footer>

    <!-- Interactive Client JavaScript -->
    <script>
        let currentTab = 'tab-sigma';

        function switchTab(tabId) {
            document.querySelectorAll('.siem-pane').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('button[id^="btn-tab-"]').forEach(btn => {
                btn.className = "px-3 py-1.5 rounded-t text-gray-400 hover:text-white";
            });

            document.getElementById(tabId).classList.remove('hidden');
            const activeBtn = document.getElementById('btn-' + tabId);
            activeBtn.className = "px-3 py-1.5 rounded-t font-semibold bg-emerald-500/20 text-emerald-400 border-b-2 border-emerald-400";
            currentTab = tabId;
        }

        function logConsole(msg, type = 'info') {
            const consoleEl = document.getElementById('live-console');
            const line = document.createElement('div');
            const timestamp = new Date().toISOString().substring(11, 19);
            let color = 'text-gray-300';
            if (type === 'success') color = 'text-emerald-400';
            if (type === 'warn') color = 'text-amber-400';
            if (type === 'danger') color = 'text-rose-400 font-bold';
            if (type === 'cyan') color = 'text-cyan-400';

            line.className = color;
            line.textContent = `[${timestamp}] ${msg}`;
            consoleEl.appendChild(line);
            consoleEl.scrollTop = consoleEl.scrollHeight;
        }

        async function synthesizeRules() {
            const threatType = document.getElementById('synth-threat-type').value;
            const ip = document.getElementById('synth-ip').value;
            const asset = document.getElementById('synth-asset').value;

            logConsole(`Synthesizing Universal Multi-SIEM rules for ${threatType} (${ip})...`, 'cyan');

            try {
                const res = await fetch('/audit/sigma', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({threat_type: threatType, source_ip: ip, target_asset: asset})
                });
                const data = await res.json();
                if (data.detection_rules) {
                    document.getElementById('code-sigma').textContent = data.detection_rules.sigma_yaml;
                    document.getElementById('code-kql').textContent = data.detection_rules.microsoft_sentinel_kql;
                    document.getElementById('code-splunk').textContent = data.detection_rules.splunk_spl;
                    document.getElementById('code-elastic').textContent = data.detection_rules.elastic_esql;
                    document.getElementById('code-aws').textContent = data.detection_rules.aws_cloudwatch;
                    logConsole(`Generated Sigma YAML, Sentinel KQL, Splunk SPL & Elastic ES|QL successfully.`, 'success');
                }
            } catch (err) {
                logConsole(`Error querying backend: ${err.message}`, 'danger');
            }
        }

        function copyCurrentRule() {
            let textToCopy = "";
            if (currentTab === 'tab-sigma') textToCopy = document.getElementById('code-sigma').textContent;
            if (currentTab === 'tab-kql') textToCopy = document.getElementById('code-kql').textContent;
            if (currentTab === 'tab-splunk') textToCopy = document.getElementById('code-splunk').textContent;
            if (currentTab === 'tab-elastic') textToCopy = document.getElementById('code-elastic').textContent;
            if (currentTab === 'tab-aws') textToCopy = document.getElementById('code-aws').textContent;

            navigator.clipboard.writeText(textToCopy);
            const copyBtnText = document.getElementById('copy-text');
            copyBtnText.textContent = "Copied!";
            setTimeout(() => { copyBtnText.textContent = "Copy Rule"; }, 1500);
            logConsole("Copied detection query to clipboard.", "success");
        }

        async function deployHoneytoken() {
            const type = document.getElementById('token-type').value;
            logConsole(`Deploying active honeytoken [${type}]...`, 'cyan');

            try {
                const res = await fetch('/deception/honeytoken', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({token_type: type, asset_name: 'prod-cluster', deployment_path: 'config/.env'})
                });
                const token = await res.json();
                
                const list = document.getElementById('honeytoken-list');
                const card = document.createElement('div');
                card.className = "p-2.5 bg-black/60 border border-slate-800 rounded flex items-center justify-between text-xs";
                card.innerHTML = `
                    <div>
                        <div class="font-mono text-amber-400 text-[11px]">${token.token_value.substring(0, 24)}...</div>
                        <div class="text-gray-400 text-[10px]">Type: ${token.token_type} • Status: <span class="text-emerald-400 font-bold">ARMED</span></div>
                    </div>
                    <button onclick="triggerBreach('${token.token_value}')" class="px-2 py-1 bg-rose-500/20 hover:bg-rose-500/40 border border-rose-500/40 text-rose-300 rounded text-[10px] transition">
                        Simulate Trip
                    </button>
                `;
                list.prepend(card);
                
                const kpi = document.getElementById('kpi-tokens');
                kpi.textContent = parseInt(kpi.textContent || "0") + 1;
                logConsole(`Honeytoken ${token.token_id} deployed and ARMED.`, 'success');
            } catch (err) {
                logConsole(`Failed to deploy token: ${err.message}`, 'danger');
            }
        }

        async function triggerBreach(tokenVal) {
            logConsole(`🚨 Attacker touched canary honeytoken! Triggering tripwire...`, 'danger');
            try {
                const res = await fetch('/deception/tripwire', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({token_value: tokenVal, source_ip: '203.0.113.88'})
                });
                const data = await res.json();
                if (data.tripwire_triggered) {
                    logConsole(`Containment Executed: IP 203.0.113.88 ISOLATED on DOCKER-USER chain!`, 'danger');
                    logConsole(`Incident ${data.incident_id} dispatched to Microsoft Sentinel & Teams.`, 'warn');
                    const drops = document.getElementById('kpi-drops');
                    drops.textContent = parseInt(drops.textContent || "0") + 1;
                }
            } catch (err) {
                logConsole(`Tripwire failed: ${err.message}`, 'danger');
            }
        }

        async function simulateAttack(type) {
            logConsole(`Dispatching simulated attack vector: ${type}...`, 'warn');
            try {
                const res = await fetch('/analyze/sync', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        service: 'sshd',
                        event_type: type === 'ssh_brute_force' ? 'ssh_failed_login' : type,
                        source_ip: '198.51.100.99',
                        raw_log: `Failed password for invalid user admin from 198.51.100.99 port 42818 ssh2`
                    })
                });
                const result = await res.json();
                if (result.threat_detected) {
                    logConsole(`Swarm Consensus: Threat CONFIRMED (${result.analysis.threat_type}). Confidence: ${result.confidence_score * 100}%`, 'danger');
                    logConsole(`Action: ${result.remediation.proposed_command}`, 'cyan');
                    const threats = document.getElementById('kpi-threats');
                    threats.textContent = parseInt(threats.textContent || "0") + 1;
                }
            } catch (err) {
                logConsole(`Simulation failed: ${err.message}`, 'danger');
            }
        }

        function approveHITL(actionId) {
            logConsole(`SecOps Administrator approved isolation for ${actionId}.`, 'success');
            document.getElementById('hitl-container').innerHTML = '<div class="text-xs text-gray-500 italic p-2">No pending high-risk containment actions.</div>';
            document.getElementById('hitl-count-badge').textContent = '0 Pending';
        }

        function rejectHITL(actionId) {
            logConsole(`SecOps Administrator dismissed action ${actionId} as false-positive.`, 'warn');
            document.getElementById('hitl-container').innerHTML = '<div class="text-xs text-gray-500 italic p-2">No pending high-risk containment actions.</div>';
            document.getElementById('hitl-count-badge').textContent = '0 Pending';
        }
    </script>
</body>
</html>
"""
