# 🛡️ Sentinel-Guard Skill for OpenClaw

> **Zero-Trust Security Supervisor & Active Tripwire Guardrail for OpenClaw powered by [Sentinel-AutoGen-Hunter](https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter)**

---

## 🎯 Overview
Autonomous AI agents like **OpenClaw** connect to real-world channels (WhatsApp, Telegram, Discord, Terminal, Filesystem). However, without strict guardrails, agents can fall victim to:
* **Indirect Prompt Injections** (manipulating LLM logic via scraped text or hostile chat messages)
* **Rogue Shell Execution** (`rm -rf /`, reverse shells, unauthorized curl payloads)
* **Credential Harvesting** (adversarial probing of `.env`, SSH keys, or cloud secrets)

The **Sentinel-Guard Skill** wraps OpenClaw in a zero-trust pre-execution perimeter. Every input and tool invocation is analyzed by the Sentinel-AutoGen-Hunter swarm in milliseconds.

---

## ⚡ Key Capabilities

1. **Pre-Execution Tool Gatekeeping**:
   - Inspects `shell`, `exec`, and file read calls before the OS executes them.
   - Blocks destructive bash patterns and unauthorized credential reads.
2. **Active Deception & Honeypot Decoys**:
   - Automatically drops signed canary honeytokens into the agent's context.
   - If an attacker attempts to extract or use them, an immediate tripwire fires.
3. **Sub-Second Kernel Containment (<400ms)**:
   - Hostile sender IP is automatically isolated via Linux Netfilter (`iptables -I DOCKER-USER`).
   - Incident is streamed to Microsoft Sentinel with full forensic KQL correlation queries.

---

## 🚀 Installation & Activation

### Step 1: Install Sentinel-AutoGen-Hunter
```bash
git clone https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter.git
cd sentinel-autogen-hunter
./install.sh
```

### Step 2: Hook into OpenClaw
```bash
python -m cli.main openclaw --install
```

### Step 3: Run OpenClaw with Active Defense
OpenClaw will now automatically invoke `guard.py` on incoming messages and tool requests.

---

**Lead Architect**: Raghav Khandal ([@raghavkhandal72-coder](https://github.com/raghavkhandal72-coder))
