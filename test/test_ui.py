# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock
import importlib.util


def test_ui_module_structure():
    """Test that ui.py has expected class structure via source inspection"""
    import ast

    # Read the source file
    with open('plugin/ui.py', 'r') as f:
        source = f.read()

    # Parse the AST
    tree = ast.parse(source)

    # Find the Main class
    main_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'Main':
            main_class = node
            break

    assert main_class is not None, "Main class not found"

    # Get all method names
    methods = [n.name for n in main_class.body if isinstance(n, ast.FunctionDef)]

    assert 'query' in methods, "query method not found"
    assert 'openUrl' in methods, "openUrl method not found"
    assert 'openMr' in methods, "openMr method not found"
    assert 'openActions' in methods, "openActions method not found"
    assert 'openIssues' in methods, "openIssues method not found"


def test_ui_imports():
    """Test that ui.py has correct imports"""
    with open('plugin/ui.py', 'r') as f:
        content = f.read()

    assert 'from flowlauncher import FlowLauncher' in content
    assert 'import webbrowser' in content
    assert 'import threading' in content
    assert 'from github_client import GitHubClient' in content
    assert 'from cache_manager import CacheManager' in content
    assert 'from chrome_profile import ChromeProfileManager' in content
    assert 'from keyring_manager import KeyringManager' in content