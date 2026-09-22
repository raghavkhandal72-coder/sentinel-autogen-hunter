"""Unit tests for OpenClaw-grade Onboarding Wizard and Pairing Manager."""

from openclaw_engine.pairing import OpenClawPairingManager
from openclaw_engine.wizard import run_onboarding_wizard


def test_pairing_manager_create_and_approve(tmp_path):
    storage_path = str(tmp_path / "pairings.json")
    mgr = OpenClawPairingManager(storage_path=storage_path)

    # 1. Initially only local companion is approved
    initial_pairings = mgr.list_pairings()
    assert initial_pairings["total_approved"] == 1
    assert mgr.is_approved("companion", "user_local") is True

    # 2. Create challenge
    chal = mgr.create_challenge(channel="telegram", sender_id="+919876543210", client_name="Phone User")
    assert len(chal["code"]) == 6
    assert mgr.is_approved("telegram", "+919876543210") is False

    # 3. Approve challenge
    res = mgr.approve_challenge(channel="telegram", code=chal["code"])
    assert res["success"] is True
    assert mgr.is_approved("telegram", "+919876543210") is True

    # 4. Challenge invalid code
    bad_res = mgr.approve_challenge(channel="telegram", code="000000")
    assert bad_res["success"] is False

    # 5. Revoke client
    rev_res = mgr.revoke_pairing("telegram")
    assert rev_res["success"] is True
    assert mgr.is_approved("telegram", "+919876543210") is False


def test_onboarding_wizard_non_interactive():
    config = run_onboarding_wizard(non_interactive=True)
    assert config is not None
    assert "model" in config
    assert "channels" in config
    assert config["shield_armed"] is True
    assert config["gateway_port"] == 8000
