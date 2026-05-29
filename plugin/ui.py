# -*- coding: utf-8 -*-
import webbrowser
import threading
import copy
from typing import List

from flowlauncher import FlowLauncher

from plugin.settings import ICON_PATH, PLUGIN_ACTION_KEYWORD
from plugin.templates import RESULT_TEMPLATE, ACTION_TEMPLATE
from github_client import GitHubClient
from cache_manager import CacheManager
from chrome_profile import ChromeProfileManager
from keyring_manager import KeyringManager


class Main(FlowLauncher):
    messages_queue = []

    def __init__(self):
        super().__init__()
        self.cache_manager = CacheManager()
        self.keyring_manager = KeyringManager()
        self.chrome_manager = ChromeProfileManager()
        # 加载配置
        self._settings = self._load_settings()

    def _load_settings(self):
        import json
        from pathlib import Path
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
        self.messages_queue = []
        q = param.strip()

        if not q:
            self._add_result(
                "GitHub Quick Access",
                "输入关键词搜索仓库，输入 gh help 查看帮助",
                method=None
            )
            return self.messages_queue

        if q.lower() == "help":
            return self._build_help_results()

        if q.lower() == "refresh":
            return self._refresh_all_accounts()

        return self._search_repositories(q)

    def _add_result(self, title: str, subtitle: str, method: str = None, parameters: list = None):
        message = copy.deepcopy(RESULT_TEMPLATE)
        message["Title"] = title
        message["SubTitle"] = subtitle
        if method and parameters is not None:
            action = copy.deepcopy(ACTION_TEMPLATE)
            action["JsonRPCAction"]["method"] = method
            action["JsonRPCAction"]["parameters"] = parameters
            message.update(action)
        self.messages_queue.append(message)

    def _search_repositories(self, keyword: str) -> List[dict]:
        results = []
        keyword_lower = keyword.lower()

        for account in self.accounts:
            token = self.keyring_manager.get_token(account.get("token_ref", ""))
            if not token:
                self._add_result(
                    f"[{account.get('alias', 'unknown')}] Token 未配置",
                    "请在设置中添加 Token",
                    method=None
                )
                continue

            cache = self.cache_manager.get_cache(account["id"], self.cache_ttl_minutes)
            if not cache:
                self._add_result(
                    f"[{account.get('alias', 'unknown')}] 缓存为空",
                    "输入 gh refresh 更新仓库列表",
                    method=None
                )
                continue

            for repo in cache.get("repositories", []):
                full_name = repo.get("full_name", "").lower()
                if keyword_lower in full_name:
                    account_alias = account.get("alias", "unknown")
                    repo_full_name = repo.get("full_name", "")
                    private_label = "私有仓库" if repo.get("is_private") else "公开仓库"
                    self._add_result(
                        f"[{account_alias}] {repo_full_name}",
                        private_label,
                        method="openUrl",
                        parameters=[account["id"], repo_full_name, "home"]
                    )

        return self.messages_queue[:self.max_results]

    def _build_help_results(self) -> List[dict]:
        self.messages_queue = []
        self._add_result("gh <关键词>", "搜索仓库", method=None)
        self._add_result("gh refresh", "刷新所有账号的仓库缓存", method=None)
        self._add_result("gh help", "显示帮助", method=None)
        return self.messages_queue

    def _refresh_all_accounts(self) -> List[dict]:
        self.messages_queue = []
        for account in self.accounts:
            self._refresh_account_cache(account)
        self._add_result("刷新完成", "所有账号的仓库缓存已更新", method=None)
        return self.messages_queue

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
            except Exception as e:
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
        except Exception as e:
            webbrowser.open(url)

    def openMr(self, account_id: str, repo_full_name: str):
        self.openUrl(account_id, repo_full_name, "mr")

    def openActions(self, account_id: str, repo_full_name: str):
        self.openUrl(account_id, repo_full_name, "actions")

    def openIssues(self, account_id: str, repo_full_name: str):
        self.openUrl(account_id, repo_full_name, "issues")