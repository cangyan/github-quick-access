# -*- coding: utf-8 -*-
import pytest
import tempfile
import shutil
from datetime import datetime
from cache_manager import CacheManager

def test_cache_manager_set_and_get():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = CacheManager(cache_dir=tmpdir)
        repos = [{"name": "test-repo", "full_name": "owner/test-repo"}]
        manager.set_cache("acc_1", repos)
        cache = manager.get_cache("acc_1")
        assert cache is not None
        assert len(cache["repositories"]) == 1
        assert cache["repositories"][0]["name"] == "test-repo"

def test_cache_manager_expiry():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = CacheManager(cache_dir=tmpdir)
        manager.set_cache("acc_1", [{"name": "test"}])
        cache = manager.get_cache("acc_1", ttl_minutes=0)
        assert cache is None

def test_cache_manager_clear():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = CacheManager(cache_dir=tmpdir)
        manager.set_cache("acc_1", [{"name": "test"}])
        manager.clear_cache("acc_1")
        cache = manager.get_cache("acc_1")
        assert cache is None

def test_get_repo_count():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = CacheManager(cache_dir=tmpdir)
        manager.set_cache("acc_1", [{"name": "r1"}, {"name": "r2"}])
        count = manager.get_repo_count("acc_1")
        assert count == 2