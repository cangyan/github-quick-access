# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch, MagicMock
from keyring_manager import KeyringManager

def test_keyring_manager_init():
    manager = KeyringManager()
    assert manager.SERVICE_NAME == "FlowLauncher.Plugin.GitHubQuickAccess"

def test_store_token_calls_keyring():
    with patch('keyring.set_password') as mock_set:
        manager = KeyringManager()
        manager.store_token("test_ref", "test_token")
        mock_set.assert_called_once_with(
            "FlowLauncher.Plugin.GitHubQuickAccess",
            "test_ref",
            "test_token"
        )

def test_get_token_calls_keyring():
    with patch('keyring.get_password', return_value="test_token"):
        manager = KeyringManager()
        token = manager.get_token("test_ref")
        assert token == "test_token"

def test_delete_token_calls_keyring():
    with patch('keyring.delete_password') as mock_delete:
        manager = KeyringManager()
        manager.delete_token("test_ref")
        mock_delete.assert_called_once_with(
            "FlowLauncher.Plugin.GitHubQuickAccess",
            "test_ref"
        )