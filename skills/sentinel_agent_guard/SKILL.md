# 🛡️ Sentinel-Agent-Guard Skill

> **Zero-Trust Security Supervisor & Active Tripwire Guardrail for Autonomous AI Agents powered by [Sentinel-AutoGen-Hunter](https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter)**

---

## 🎯 Purpose

Autonomous AI agents connect to real-world channels (Messaging APIs, Terminal, Filesystem, Cloud Tools). Without strict pre-execution guardrails, agents are vulnerable to:
1. **Indirect Prompt Injections**: Hidden instructions inside ingested web pages, PDFs, or user messages that hijack the agent's system prompt.
2. **Destructive Tool Execution**: Catastrophic commands like `rm -rf /`, fork bombs, or raw disk overwriting executed via agent terminal tools.
3. **Credential Harvesting**: Attacker prompts requesting `/etc/shadow`, AWS keys, or `.env` files.
4. **Adversarial Probing**: Automated crawlers and red-team scanners poking the agent's memory.

The **Sentinel-Agent-Guard Skill** wraps the agent in a zero-trust pre-execution perimeter. Every input and tool invocation is analyzed by the Sentinel-AutoGen-Hunter security swarm in milliseconds.

---

## ⚡ Architecture Flow

```
Attacker / User Input
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  Sentinel Agent Guard (on_user_message)                 │
│  - Prompt Injection Scanner (<3ms)                       │
│  - Active Canary Honeytoken Verification                 │
└──────────────┬───────────────────────────┬───────────────┘
               │ Passed                    │ Attack Detected
               ▼                           ▼
┌──────────────────────────────┐    ┌──────────────────────────────────┐
│   Autonomous LLM Reasoning   │    │ Sentinel Netfilter Containment   │
│   (AutoGen / Swarms)         │    │ - iptables -I DOCKER-USER DROP   │
└──────────────┬───────────────┘    │ - Log to Sentinel Log Analytics  │
               │ Tool Call          └──────────────────────────────────┘
               ▼
┌──────────────────────────────────────────────────────────┐
│  Sentinel Pre-Execution Guard (on_before_tool_execute)   │
│  - Destructive Command Blocker (rm -rf, reverse shells)   │
│  - Credential & Shadow File Protection                   │
└──────────────────────────────────────────────────────────┘
```

---

## 📦 Quick Installation

```bash
# 1. Install & enable Sentinel Agent Guard
python -m cli.main shield --install

# 2. Run active defense injection simulation
python -m cli.main shield --test-injection

# 3. View active defenses & armed canary tripwires
python -m cli.main shield --status
```
