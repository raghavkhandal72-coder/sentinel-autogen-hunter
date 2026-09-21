"""Main CLI entrypoint for Sentinel-AutoGen-Hunter.

Provides commands:
  sentinel-hunter tui         - Launch Cyberpunk Terminal Radar console
  sentinel-hunter dashboard   - Start FastAPI server and open Web SOC Dashboard
  sentinel-hunter sigma       - Synthesize Sigma, KQL, SPL, and ES|QL detection queries
  sentinel-hunter canary      - Generate cryptographic canary honeytokens
  sentinel-hunter test        - Run complete offline 67-test verification suite
"""

import argparse
import sys
import webbrowser


def main():
    parser = argparse.ArgumentParser(
        prog="sentinel-hunter",
        description="Sentinel-AutoGen-Hunter: Cloud-Native Autonomous Threat Hunter",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. TUI Command
    subparsers.add_parser("tui", help="Launch interactive Cyberpunk Terminal Radar")

    # 2. Dashboard Command
    dash_parser = subparsers.add_parser("dashboard", help="Start Web SOC Operations Center")
    dash_parser.add_argument("--port", type=int, default=8000, help="Port to bind server (default: 8000)")
    dash_parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser")

    # 3. Sigma Command
    sigma_parser = subparsers.add_parser("sigma", help="Synthesize Universal Multi-SIEM Sigma rules")
    sigma_parser.add_argument("--threat", type=str, default="ssh_brute_force", help="Threat classification")
    sigma_parser.add_argument("--ip", type=str, default="198.51.100.42", help="Attacker IP address")
    sigma_parser.add_argument("--asset", type=str, default="prod-ingress", help="Target asset")
    sigma_parser.add_argument("--format", type=str, choices=["all", "sigma", "kql", "splunk", "elastic", "aws"], default="all")

    # 4. Canary Command
    canary_parser = subparsers.add_parser("canary", help="Deploy active defense canary honeytokens")
    canary_parser.add_argument("--type", choices=["aws_key", "github_token", "azure_secret", "db_connection"], default="aws_key")
    canary_parser.add_argument("--asset", default="production-db")
    canary_parser.add_argument("--path", default="config/.env")

    # 5. Test Command
    subparsers.add_parser("test", help="Run 67-test verification suite")

    args = parser.parse_args()

    if args.command == "tui":
        from .tui import run_interactive_tui
        run_interactive_tui()

    elif args.command == "dashboard":
        import uvicorn
        from agents.orchestrator import app

        url = f"http://localhost:{args.port}/dashboard"
        print(f"\n🛡️ Starting Sentinel-AutoGen-Hunter Web SOC Dashboard at {url}")
        if not args.no_browser:
            webbrowser.open(url)
        uvicorn.run(app, host="0.0.0.0", port=args.port)

    elif args.command == "sigma":
        from agents.sigma_engine import synthesize_universal_matrix

        res = synthesize_universal_matrix({"threat_type": args.threat, "attacker_ip": args.ip, "target_asset": args.asset})
        rules = res["detection_rules"]
        if args.format == "all" or args.format == "sigma":
            print("\n[ SIGMA YAML ]\n" + rules["sigma_yaml"])
        if args.format == "all" or args.format == "kql":
            print("\n[ MICROSOFT SENTINEL KQL ]\n" + rules["microsoft_sentinel_kql"])
        if args.format == "all" or args.format == "splunk":
            print("\n[ SPLUNK SPL ]\n" + rules["splunk_spl"])
        if args.format == "all" or args.format == "elastic":
            print("\n[ ELASTIC ES|QL ]\n" + rules["elastic_esql"])
        if args.format == "all" or args.format == "aws":
            print("\n[ AWS CLOUDWATCH ]\n" + rules["aws_cloudwatch"])

    elif args.command == "canary":
        from agents.deception_engine import generate_honeytoken

        token = generate_honeytoken(args.type, args.asset, args.path)
        print(f"\n[+] Deployed Honeytoken: {token['token_id']}")
        print(f"    Type   : {token['token_type']}")
        print(f"    Value  : {token['token_value']}")
        print(f"    Status : {token['status']}\n")

    elif args.command == "test":
        import pytest
        sys.exit(pytest.main(["tests/", "-v"]))

    else:
        # Default behavior when run with no arguments: open TUI
        from .tui import run_interactive_tui
        run_interactive_tui()


if __name__ == "__main__":
    main()
