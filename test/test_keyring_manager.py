# -*- coding: utf-8 -*-
import pytest
import tempfile
import os
from keyring_manager import KeyringManager

def test_keyring_manager_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "settings.json")
        manager = KeyringManager(settings_path=path)
        assert manager.settings_path.name == "settings.json"

def test_store_and_get_token():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "settings.json")
        manager = KeyringManager(settings_path=path)
        manager.store_token("test_ref", "fake_token")
        token = manager.get_token("test_ref")
        assert token == "fake_token"

def test_get_nonexistent_token():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "settings.json")
        manager = KeyringManager(settings_path=path)
        token = manager.get_token("nonexistent")
        assert token is None

def test_delete_token():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "settings.json")
        manager = KeyringManager(settings_path=path)
        manager.store_token("test_ref", "fake_token")
        manager.delete_token("test_ref")
        assert manager.get_token("test_ref") is None