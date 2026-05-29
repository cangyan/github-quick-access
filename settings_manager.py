# -*- coding: utf-8 -*-
import json
import uuid
from pathlib import Path
from typing import List, Optional
from chrome_profile import ChromeProfileManager
from keyring_manager import KeyringManager


class SettingsManager:
    """插件配置管理"""

    def __init__(self, settings_path: Optional[str] = None):
        if settings_path:
            self.settings_path = Path(settings_path)
        else:
            self.settings_path = Path(__file__).parent / "settings.json"
        self.keyring_manager = KeyringManager()
        self._settings = self._load()

    def _load(self) -> dict:
        if self.settings_path.exists():
            with open(self.settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"accounts": [], "cache_ttl_minutes": 30, "max_results": 20}

    def save(self):
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=2, ensure_ascii=False)

    @property
    def accounts(self) -> List[dict]:
        return self._settings.get("accounts", [])

    @property
    def cache_ttl_minutes(self) -> int:
        return self._settings.get("cache_ttl_minutes", 30)

    @property
    def max_results(self) -> int:
        return self._settings.get("max_results", 20)

    def add_account(self, alias: str, token: str, chrome_profile_path: str, organizations: List[str]) -> dict:
        """添加新账号"""
        account_id = f"acc_{uuid.uuid4().hex[:8]}"
        token_ref = f"github_{account_id}"
        self.keyring_manager.store_token(token_ref, token)
        account = {
            "id": account_id,
            "alias": alias,
            "token_ref": token_ref,
            "chrome_profile_path": chrome_profile_path,
            "organizations": organizations
        }
        self._settings.setdefault("accounts", []).append(account)
        self.save()
        return account

    def remove_account(self, account_id: str):
        """删除账号"""
        account = next((a for a in self.accounts if a["id"] == account_id), None)
        if account:
            self.keyring_manager.delete_token(account.get("token_ref", ""))
        self._settings["accounts"] = [a for a in self.accounts if a["id"] != account_id]
        self.save()

    def update_account(self, account_id: str, **updates):
        """更新账号配置（不包括 token）"""
        for i, acc in enumerate(self._settings.get("accounts", [])):
            if acc["id"] == account_id:
                if "alias" in updates:
                    self._settings["accounts"][i]["alias"] = updates["alias"]
                if "chrome_profile_path" in updates:
                    self._settings["accounts"][i]["chrome_profile_path"] = updates["chrome_profile_path"]
                if "organizations" in updates:
                    self._settings["accounts"][i]["organizations"] = updates["organizations"]
                break
        self.save()

    def detect_chrome_profiles(self) -> List[dict]:
        """检测可用的 Chrome Profile"""
        manager = ChromeProfileManager()
        return manager.detect_profiles()

    def get_account_by_id(self, account_id: str) -> Optional[dict]:
        """根据 ID 获取账号"""
        return next((a for a in self.accounts if a["id"] == account_id), None)