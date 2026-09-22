"""OpenClaw-Grade Device & Channel Pairing Protocol for Sentinel-AutoGen-Hunter.

Manages deterministic approval of unknown incoming senders and companion clients
using cryptographic 6-digit challenge tokens and zero-trust session vouchers.
"""

import json
import os
import secrets
import time
from pathlib import Path
from typing import Any


class OpenClawPairingManager:
    """Manages multi-channel DM and companion app pairing state."""

    def __init__(self, storage_path: str | None = None):
        if storage_path:
            self.storage_file = Path(storage_path)
        else:
            home = Path.home() / ".sentinel"
            home.mkdir(parents=True, exist_ok=True)
            self.storage_file = home / "pairings.json"

        self.pending_challenges: dict[str, dict[str, Any]] = {}
        self.approved_clients: list[dict[str, Any]] = [
            {
                "client_id": "sentinel-local-companion",
                "client_name": "Windows Companion (Localhost)",
                "channel": "companion",
                "approved_at": int(time.time()),
                "status": "ACTIVE",
            }
        ]
        self._load()

    def _load(self):
        """Loads persistent pairings from disk."""
        if self.storage_file.exists():
            try:
                data = json.loads(self.storage_file.read_text(encoding="utf-8"))
                self.approved_clients = data.get("approved_clients", self.approved_clients)
                self.pending_challenges = data.get("pending_challenges", {})
            except Exception:
                pass

    def _save(self):
        """Persists pairing list to disk."""
        try:
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            self.storage_file.write_text(
                json.dumps(
                    {
                        "approved_clients": self.approved_clients,
                        "pending_challenges": self.pending_challenges,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except Exception:
            pass

    def create_challenge(
        self, channel: str, sender_id: str, client_name: str | None = None
    ) -> dict[str, Any]:
        """Creates a 6-digit challenge code for an unverified sender or device."""
        self._load()
        code = f"{secrets.randbelow(900000) + 100000}"  # 6-digit code e.g. 482910
        key = f"{channel}:{sender_id}"
        challenge = {
            "channel": channel,
            "sender_id": sender_id,
            "client_name": client_name or f"{channel.capitalize()} User ({sender_id})",
            "code": code,
            "created_at": int(time.time()),
            "expires_at": int(time.time()) + 600,  # 10 minutes
        }
        self.pending_challenges[key] = challenge
        self._save()
        return challenge

    def approve_challenge(self, channel: str, code: str) -> dict[str, Any]:
        """Validates and approves a pending 6-digit challenge code."""
        self._load()
        code = str(code).strip()
        matched_key = None
        target_challenge = None

        # Clean expired
        now = int(time.time())
        for k, v in list(self.pending_challenges.items()):
            if v["expires_at"] < now:
                del self.pending_challenges[k]

        for k, v in self.pending_challenges.items():
            if v["channel"].lower() == channel.lower() and v["code"] == code:
                matched_key = k
                target_challenge = v
                break

        if not target_challenge:
            return {
                "success": False,
                "message": f"Invalid or expired pairing code '{code}' for channel '{channel}'."
            }

        client_entry = {
            "client_id": f"cli-{secrets.token_hex(4)}",
            "client_name": target_challenge["client_name"],
            "channel": target_challenge["channel"],
            "sender_id": target_challenge["sender_id"],
            "approved_at": now,
            "status": "ACTIVE",
            "session_token": f"sec_voucher_{secrets.token_urlsafe(16)}",
        }
        self.approved_clients.append(client_entry)
        del self.pending_challenges[matched_key]
        self._save()

        return {
            "success": True,
            "message": f"Successfully approved {client_entry['client_name']} on channel {channel}!",
            "client": client_entry,
        }

    def list_pairings(self) -> dict[str, Any]:
        """Returns all approved devices and pending challenges."""
        now = int(time.time())
        valid_pending = [
            c for c in self.pending_challenges.values() if c["expires_at"] >= now
        ]
        return {
            "total_approved": len(self.approved_clients),
            "approved": self.approved_clients,
            "total_pending": len(valid_pending),
            "pending": valid_pending,
        }

    def revoke_pairing(self, identifier: str) -> dict[str, Any]:
        """Revokes an approved client by client_id, client_name, sender_id, or channel."""
        self._load()
        initial_len = len(self.approved_clients)
        ident_lower = identifier.lower().strip()
        self.approved_clients = [
            c
            for c in self.approved_clients
            if ident_lower not in c.get("client_id", "").lower()
            and ident_lower not in c.get("client_name", "").lower()
            and ident_lower not in c.get("sender_id", "").lower()
            and ident_lower != c.get("channel", "").lower()
        ]
        if len(self.approved_clients) < initial_len:
            self._save()
            return {"success": True, "message": f"Revoked pairing for '{identifier}'."}
        return {"success": False, "message": f"No client matched identifier '{identifier}'."}

    def is_approved(self, channel: str, sender_id: str) -> bool:
        """Checks if a sender is authorized on a given channel."""
        for c in self.approved_clients:
            if c.get("channel") == channel and c.get("sender_id") == sender_id:
                return True
            if c.get("channel") == "companion" and sender_id == "user_local":
                return True
        return False


pairing_manager = OpenClawPairingManager()
