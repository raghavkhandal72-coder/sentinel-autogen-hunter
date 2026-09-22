"""Tests for Automated Adversary Emulation & Attack Simulator."""

from agents.attack_simulator import attack_simulator


def test_simulate_individual_campaigns():
    campaigns = ["ssh_brute_force", "prompt_injection", "kubernetes_escape", "canary_tripwire"]
    for c in campaigns:
        res = attack_simulator.simulate_campaign(c)
        assert res["campaign"] == c
        assert res["status"] in ["CONTAINED", "BLOCKED", "INTERCEPTED"]
        assert res["threat_detected"] is True
        assert res["containment_latency_ms"] >= 0.0


def test_run_all_campaigns():
    summary = attack_simulator.run_all_campaigns()
    assert summary["total_campaigns_executed"] == 4
    assert summary["threats_neutralized"] == 4
    assert summary["mitigation_success_rate"] == "100.0%"
    assert summary["average_containment_latency_ms"] < 100.0
    assert len(summary["results"]) == 4


def test_unknown_campaign():
    res = attack_simulator.simulate_campaign("non_existent_exploit")
    assert res["status"] == "error"
    assert "Unknown campaign" in res["message"]
