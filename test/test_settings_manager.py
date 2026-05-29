# -*- coding: utf-8 -*-
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from settings_manager import SettingsManager


def test_settings_manager_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SettingsManager(settings_path=os.path.join(tmpdir, "settings.json"))
        assert sm.accounts == []
        assert sm.cache_ttl_minutes == 30
        assert sm.max_results == 20


def test_add_account():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SettingsManager(settings_path=os.path.join(tmpdir, "settings.json"))
        with patch.object(sm.keyring_manager, 'store_token'):
            account = sm.add_account(
                alias="Test",
                token="fake_token",
                chrome_profile_path="/path/to/profile",
                organizations=["org1"]
            )
            assert account["alias"] == "Test"
            assert account["id"].startswith("acc_")
            assert len(sm.accounts) == 1


def test_remove_account():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SettingsManager(settings_path=os.path.join(tmpdir, "settings.json"))
        with patch.object(sm.keyring_manager, 'store_token'):
            account = sm.add_account("Test", "token", "/path", [])
        with patch.object(sm.keyring_manager, 'delete_token'):
            sm.remove_account(account["id"])
        assert len(sm.accounts) == 0