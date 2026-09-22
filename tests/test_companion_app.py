"""Tests for Sentinel Windows Companion Desktop Application."""

import pytest


def test_companion_app_initialization():
    """Validates that the Sentinel Windows Companion initializes all UI tabs without crashing."""
    try:
        import tkinter
        # Test if a display server is active
        root = tkinter.Tk()
        root.destroy()
    except Exception as exc:
        pytest.skip(f"Skipping GUI test on headless environment without display: {exc}")

    from gui.companion_app import SentinelWindowsCompanion

    app = SentinelWindowsCompanion()
    try:
        assert app.title() == "Sentinel Windows Companion"
        assert app.active_tab == "connection"
        assert app.is_connected is False

        # Test switching tabs
        tabs = ["connection", "swarm", "shield", "canary", "simulator", "mitre", "diagnostics", "settings"]
        for tab in tabs:
            app.select_tab(tab)
            assert app.active_tab == tab

        # Test toggle gateway connection
        app.toggle_gateway_connection()
        assert app.is_connected is True
        assert "Connected" in app.status_pill.cget("text")

        app.toggle_gateway_connection()
        assert app.is_connected is False
    finally:
        app.destroy()
