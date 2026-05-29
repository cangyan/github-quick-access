# -*- coding: utf-8 -*-
from github_client import GitHubClient

def test_github_client_init():
    client = GitHubClient("fake_token")
    assert client.token == "fake_token"
    assert client.BASE_URL == "https://api.github.com"

def test_get_user_repos_method_exists():
    client = GitHubClient("fake_token")
    assert hasattr(client, "get_user_repos")
    assert callable(client.get_user_repos)

def test_get_org_repos_method_exists():
    client = GitHubClient("fake_token")
    assert hasattr(client, "get_org_repos")
    assert callable(client.get_org_repos)

def test_get_all_repos_for_account_method_exists():
    client = GitHubClient("fake_token")
    assert hasattr(client, "get_all_repos_for_account")
    assert callable(client.get_all_repos_for_account)

def test_validate_token_method_exists():
    client = GitHubClient("fake_token")
    assert hasattr(client, "validate_token")
    assert callable(client.validate_token)