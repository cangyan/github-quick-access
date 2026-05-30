# -*- coding: utf-8 -*-
import webbrowser
import threading
import copy
import json
from pathlib import Path
from typing import List

from plugin.settings import ICON_PATH
from github_client import GitHubClient
from cache_manager import CacheManager
from chrome_profile import ChromeProfileManager
from keyring_manager import KeyringManager

# --- i18n ---
_ui_translations: dict = {}
_ui_locale: str = "en"

def _load_ui_translations():
    global _ui_translations
    trans_dir = Path(__file__).parent / "translations"
    for f in trans_dir.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            _ui_translations[f.stem] = json.load(fp)

def _t(key: str, locale: str = None) -> str:
    loc = locale or _ui_locale
    return _ui_translations.get(loc, {}).get(key, _ui_translations.get("en", {}).get(key, key))

def _detect_locale():
    settings_path = Path(__file__).parent.parent / "settings.json"
    if settings_path.exists():
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                lang = data.get("language", "en")
                if lang in ("en", "zh", "ja"):
                    return lang
        except:
            pass
    return "en"

_load_ui_translations()
_ui_locale = _detect_locale()


class Main:
    """GitHub Quick Access 插件主类"""

    def __init__(self):
        self.cache_manager = CacheManager()
        self.keyring_manager = KeyringManager()
        self.chrome_manager = ChromeProfileManager()
        self._settings = self._load_settings()

    def _load_settings(self):
        settings_path = Path(__file__).parent.parent / "settings.json"
        if settings_path.exists():
            with open(settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"accounts": [], "cache_ttl_minutes": 30, "max_results": 20}

    @property
    def accounts(self):
        return self._settings.get("accounts", [])

    @property
    def cache_ttl_minutes(self):
        return self._settings.get("cache_ttl_minutes", 30)

    @property
    def max_results(self):
        return self._settings.get("max_results", 20)

    def query(self, param: str) -> List[dict]:
        results = []
        q = param.strip()

        if not q:
            return [{
                "Title": _t("plugin_name"),
                "SubTitle": _t("search_placeholder"),
                "IcoPath": ICON_PATH,
            }]

        if q.lower() == "help":
            return [
                {"Title": "gh <keyword>", "SubTitle": _t("help_search"), "IcoPath": ICON_PATH},
                {"Title": "gh refresh", "SubTitle": _t("help_refresh"), "IcoPath": ICON_PATH},
                {"Title": "gh help", "SubTitle": _t("help_show"), "IcoPath": ICON_PATH},
            ]

        if q.lower() == "refresh":
            for account in self.accounts:
                self._refresh_account_cache(account)
            return [{"Title": _t("refresh_done"), "SubTitle": _t("refresh_done_subtitle"), "IcoPath": ICON_PATH}]

        results = []
        keyword_lower = q.lower()

        for account in self.accounts:
            token = self.keyring_manager.get_token(account.get("token_ref", ""))
            if not token:
                results.append({
                    "Title": f"[{account.get('alias', 'unknown')}] {_t('token_unconfigured')}",
                    "SubTitle": _t("token_hint"),
                    "IcoPath": ICON_PATH,
                })
                continue

            cache = self.cache_manager.get_cache(account["id"], self.cache_ttl_minutes)
            if not cache:
                results.append({
                    "Title": f"[{account.get('alias', 'unknown')}] {_t('cache_empty')}",
                    "SubTitle": _t("cache_hint"),
                    "IcoPath": ICON_PATH,
                })
                continue

            for repo in cache.get("repositories", []):
                full_name = repo.get("full_name", "").lower()
                if keyword_lower in full_name:
                    account_alias = account.get("alias", "unknown")
                    repo_full_name = repo.get("full_name", "")
                    private_label = _t("private_repo") if repo.get("is_private") else _t("public_repo")
                    results.append({
                        "Title": f"▶ [{account_alias}] {repo_full_name}",
                        "SubTitle": f"{private_label} - {_t('home')}",
                        "IcoPath": ICON_PATH,
                        "JsonRPCAction": {
                            "method": "openUrl",
                            "parameters": [account["id"], repo_full_name, "home"]
                        }
                    })
                    results.append({
                        "Title": f"🔀 [{account_alias}] {repo_full_name} - {_t('mr')}",
                        "SubTitle": f"{private_label} - Merge Requests",
                        "IcoPath": ICON_PATH,
                        "JsonRPCAction": {
                            "method": "openUrl",
                            "parameters": [account["id"], repo_full_name, "mr"]
                        }
                    })
                    results.append({
                        "Title": f"⚡ [{account_alias}] {repo_full_name} - {_t('actions')}",
                        "SubTitle": f"{private_label} - {_t('actions')}",
                        "IcoPath": ICON_PATH,
                        "JsonRPCAction": {
                            "method": "openUrl",
                            "parameters": [account["id"], repo_full_name, "actions"]
                        }
                    })
                    results.append({
                        "Title": f"📋 [{account_alias}] {repo_full_name} - {_t('issues')}",
                        "SubTitle": f"{private_label} - {_t('issues')}",
                        "IcoPath": ICON_PATH,
                        "JsonRPCAction": {
                            "method": "openUrl",
                            "parameters": [account["id"], repo_full_name, "issues"]
                        }
                    })

        # 按 repo_full_name 去重，保留每个仓库的第一条结果（主页优先）
        seen = set()
        unique_results = []
        for r in results:
            repo_name = r.get("JsonRPCAction", {}).get("parameters", [None])[1] or ""
            if repo_name and repo_name not in seen:
                seen.add(repo_name)
                unique_results.append(r)

        return unique_results[:self.max_results]

    def _refresh_account_cache(self, account):
        def _do_refresh():
            token = self.keyring_manager.get_token(account.get("token_ref", ""))
            if not token:
                return
            try:
                client = GitHubClient(token)
                repos = client.get_all_repos_for_account(account.get("organizations", []))
                simplified = [{
                    "name": r.get("name", ""),
                    "full_name": r.get("full_name", ""),
                    "url": r.get("html_url", ""),
                    "is_private": r.get("private", False),
                    "org": r.get("owner", {}).get("login", "")
                } for r in repos]
                self.cache_manager.set_cache(account["id"], simplified)
            except Exception:
                pass

        thread = threading.Thread(target=_do_refresh)
        thread.start()

    def openUrl(self, account_id: str, repo_full_name: str, page: str):
        """JSON-RPC action: 打开仓库页面"""
        account = next((a for a in self.accounts if a["id"] == account_id), None)
        if not account:
            return

        url = self.chrome_manager.build_url(repo_full_name, page)
        profile_path = account.get("chrome_profile_path", "")
        try:
            self.chrome_manager.open_url(profile_path, url)
        except Exception:
            webbrowser.open(url)