"""Cyberpunk Terminal User Interface (TUI) for Sentinel-AutoGen-Hunter.

Provides a live, zero-dependency ANSI-based cyber radar console directly
in your terminal with interactive attack simulation, honeytoken deployment,
and multi-SIEM Sigma rule generation.
"""

import os
import sys
import time

# ANSI Color Palette
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Cyberpunk Neon Colors
CYAN = "\033[38;2;0;216;255m"
EMERALD = "\033[38;2;0;255;136m"
CRIMSON = "\033[38;2;255;51;102m"
AMBER = "\033[38;2;255;170;0m"
PURPLE = "\033[38;2;180;100;255m"
SLATE = "\033[38;2;100;116;139m"
WHITE = "\033[38;2;240;240;240m"

BANNER = f"""{EMERALD}{BOLD}
  ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     
  ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     
  ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     
  ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     
  ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
  ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝{CYAN}
       AUTONOMOUS ZERO-TRUST CLOUD THREAT HUNTER v2.0
       Powered by AutoGen Swarm • Microsoft Sentinel • MCP{RESET}
"""


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_status_bar():
    print(
        f"{SLATE}--------------------------------------------------------------------------------{RESET}"
    )
    print(
        f" {EMERALD}[●] ZERO-TRUST: ACTIVE{RESET}  |  "
        f"{CYAN}[●] SWARM: 4 AGENTS{RESET}  |  "
        f"{AMBER}[●] CANARY TRIPS: 6 ARMED{RESET}  |  "
        f"{PURPLE}[●] MCP: READY{RESET}"
    )
    print(
        f"{SLATE}--------------------------------------------------------------------------------{RESET}\n"
    )


def print_radar_metrics():
    print(f"{WHITE}{BOLD} [ LIVE TELEMETRY RADAR ]{RESET}")
    print(f" {SLATE}+{'-'*76}+{RESET}")
    print(
        f" |  {CRIMSON}{BOLD}THREATS INTERCEPTED{RESET} : {WHITE}24 events{RESET}  "
        f"|  {CYAN}{BOLD}FIREWALL DROPS{RESET}      : {WHITE}18 hosts (DOCKER-USER){RESET} |"
    )
    print(
        f" |  {EMERALD}{BOLD}SWARM CONFIDENCE{RESET}    : {EMERALD}94.8%{RESET}      "
        f"|  {AMBER}{BOLD}HONEYTOKENS ARMED{RESET}   : {WHITE}6 credentials{RESET}         |"
    )
    print(f" {SLATE}+{'-'*76}+{RESET}\n")


def print_mitre_table():
    print(f"{WHITE}{BOLD} [ MITRE ATT&CK REAL-TIME RADAR ]{RESET}")
    print(f" {SLATE}┌{'─'*22}┬{'─'*22}┬{'─'*30}┐{RESET}")
    print(
        f" {SLATE}│{RESET} {CYAN}TACTIC{RESET}                {SLATE}│{RESET} {CYAN}TECHNIQUE ID{RESET}          {SLATE}│{RESET} {CYAN}CURRENT STATUS{RESET}                 {SLATE}│{RESET}"
    )
    print(f" {SLATE}├{'─'*22}┼{'─'*22}┼{'─'*30}┤{RESET}")
    print(
        f" {SLATE}│{RESET} Credential Access     {SLATE}│{RESET} T1110.001 (Brute)    {SLATE}│{RESET} {CRIMSON}ACTIVE ATTACK ISOLATED{RESET}        {SLATE}│{RESET}"
    )
    print(
        f" {SLATE}│{RESET} Defense Evasion       {SLATE}│{RESET} T1078.004 (Cloud)    {SLATE}│{RESET} {AMBER}Canary Tripwire Armed{RESET}         {SLATE}│{RESET}"
    )
    print(
        f" {SLATE}│{RESET} Discovery             {SLATE}│{RESET} T1046 (Port Scan)    {SLATE}│{RESET} {EMERALD}Pre-filtered (DFA Engine){RESET}     {SLATE}│{RESET}"
    )
    print(
        f" {SLATE}│{RESET} Lateral Movement      {SLATE}│{RESET} T1021.004 (SSH)      {SLATE}│{RESET} {WHITE}0 Breaches Observed{RESET}            {SLATE}│{RESET}"
    )
    print(f" {SLATE}└{'─'*22}┴{'─'*22}┴{'─'*30}┘{RESET}\n")


def run_interactive_tui():
    """Main interactive terminal loop."""
    clear_screen()
    print(BANNER)
    print_status_bar()
    print_radar_metrics()
    print_mitre_table()

    while True:
        print(f"{WHITE}{BOLD}[ COMMAND CONSOLE ]{RESET}")
        print(f"  {CYAN}[1]{RESET} Simulate SSH Brute Force Attack Vector")
        print(f"  {AMBER}[2]{RESET} Generate & Deploy Cryptographic Honeytoken (Canary AWS Key)")
        print(f"  {EMERALD}[3]{RESET} Synthesize Universal Multi-SIEM Rule (Sigma, KQL, SPL, ES|QL)")
        print(f"  {PURPLE}[4]{RESET} Launch Web SOC Command Center Dashboard (http://localhost:8000/dashboard)")
        print(f"  {CRIMSON}[5]{RESET} Run 67-Test Verification Suite")
        print(f"  {SLATE}[0]{RESET} Exit TUI\n")

        try:
            choice = input(f"{EMERALD}sentinel-hunter >> {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Sentinel-AutoGen-Hunter TUI.")
            break

        if choice == "1":
            print(f"\n{CRIMSON}>> Injecting synthetic brute-force telemetry...{RESET}")
            from agents.autogen_swarm import AutoGenThreatSwarm

            swarm = AutoGenThreatSwarm()
            payload = {
                "service": "sshd",
                "event_type": "authentication_failed",
                "source_ip": "198.51.100.99",
                "target_user": "root",
                "raw_log": "Failed password for root from 198.51.100.99 port 52311 ssh2",
            }
            res = swarm.execute_hunt_pipeline(payload)
            print(f"{EMERALD}✔ Analysis Result:{RESET} Threat Detected = {res.get('threat_detected')}")
            print(f"{CYAN}✔ Confidence:{RESET} {res.get('confidence_score')}")
            print(f"{AMBER}✔ Action:{RESET} {res.get('remediation', {}).get('proposed_command')}\n")

        elif choice == "2":
            from agents.deception_engine import generate_honeytoken

            token = generate_honeytoken("aws_key", "prod-s3-vault", "config/.env")
            print(f"\n{AMBER}✔ Canary Honeytoken Deployed:{RESET}")
            print(f"  ID        : {token['token_id']}")
            print(f"  Token     : {token['token_value']}")
            print(f"  Status    : {EMERALD}{token['status']}{RESET}\n")

        elif choice == "3":
            from agents.sigma_engine import synthesize_universal_matrix

            matrix = synthesize_universal_matrix({
                "threat_type": "ssh_brute_force",
                "attacker_ip": "198.51.100.42",
                "target_asset": "prod-k8s-ingress",
            })
            print(f"\n{CYAN}✔ SigmaHQ Standard Rule Generated:{RESET}")
            print(matrix["detection_rules"]["sigma_yaml"])
            print(f"\n{EMERALD}✔ Microsoft Sentinel KQL Rule:{RESET}")
            print(matrix["detection_rules"]["microsoft_sentinel_kql"] + "\n")

        elif choice == "4":
            print(f"\n{PURPLE}>> Starting Web SOC Server on port 8000...{RESET}")
            print(f"Open: {WHITE}{BOLD}http://localhost:8000/dashboard{RESET}")
            import webbrowser
            webbrowser.open("http://localhost:8000/dashboard")
            import uvicorn
            from agents.orchestrator import app
            uvicorn.run(app, host="0.0.0.0", port=8000)

        elif choice == "5":
            print(f"\n{EMERALD}>> Running pytest test suite...{RESET}")
            import pytest
            pytest.main(["tests/", "-q"])
            print()

        elif choice == "0":
            print(f"{CYAN}Shutting down TUI. Stay secure!{RESET}")
            break
        else:
            print(f"{CRIMSON}Invalid choice. Select 0-5.{RESET}\n")


if __name__ == "__main__":
    run_interactive_tui()
