# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone

class CacheManager:
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path(__file__).parent / "cache"
        self.cache_dir.mkdir(exist_ok=True)

    def _cache_path(self, account_id: str) -> Path:
        return self.cache_dir / f"{account_id}.json"

    def get_cache(self, account_id: str, ttl_minutes: int = 30) -> Optional[Dict]:
        """获取缓存，过期返回 None"""
        cache_path = self._cache_path(account_id)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)

            updated_at = datetime.fromisoformat(cache.get("updated_at", "2000-01-01T00:00:00+00:00")).astimezone(timezone.utc)
            if datetime.now(timezone.utc) - updated_at > timedelta(minutes=ttl_minutes):
                return None

            return cache
        except:
            return None

    def set_cache(self, account_id: str, repositories: List[Dict]):
        """设置缓存"""
        cache_path = self._cache_path(account_id)
        cache = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "repositories": repositories
        }
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)

    def clear_cache(self, account_id: str):
        """清除指定账号的缓存"""
        cache_path = self._cache_path(account_id)
        if cache_path.exists():
            cache_path.unlink()

    def clear_all(self):
        """清除所有缓存"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()

    def get_repo_count(self, account_id: str) -> int:
        """获取缓存中的仓库数量"""
        cache = self.get_cache(account_id)
        if cache:
            return len(cache.get("repositories", []))
        return 0