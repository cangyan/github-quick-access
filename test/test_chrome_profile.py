# -*- coding: utf-8 -*-
import pytest
from chrome_profile import ChromeProfileManager

def test_chrome_profile_manager_init():
    manager = ChromeProfileManager()
    assert hasattr(manager, "detect_profiles")
    assert hasattr(manager, "open_url")
    assert hasattr(manager, "get_chrome_executable")

def test_build_url_home():
    url = ChromeProfileManager.build_url("owner/repo", "home")
    assert url == "https://github.com/owner/repo"

def test_build_url_mr():
    url = ChromeProfileManager.build_url("owner/repo", "mr")
    assert url == "https://github.com/owner/repo/pulls"

def test_build_url_actions():
    url = ChromeProfileManager.build_url("owner/repo", "actions")
    assert url == "https://github.com/owner/repo/actions"

def test_build_url_issues():
    url = ChromeProfileManager.build_url("owner/repo", "issues")
    assert url == "https://github.com/owner/repo/issues"