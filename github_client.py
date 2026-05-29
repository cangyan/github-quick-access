# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Dict, Optional


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.token = token

    def _make_request(self, url: str, params: dict = None) -> dict:
        """发送 GET 请求并返回 JSON 数据"""
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"

        req = urllib.request.Request(url)
        req.add_header("Authorization", f"token {self.token}")
        req.add_header("Accept", "application/vnd.github.v3+json")

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            raise Exception(f"GitHub API error: {e.code} {error_body}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_user_repos(self, per_page: int = 100) -> List[Dict]:
        """获取当前用户的仓库（包括私有）"""
        repos = []
        page = 1
        while True:
            data = self._make_request(
                f"{self.BASE_URL}/user/repos",
                params={"per_page": per_page, "page": page, "sort": "updated"}
            )
            if not data:
                break
            repos.extend(data)
            if len(data) < per_page:
                break
            page += 1
        return repos

    def get_org_repos(self, org: str, per_page: int = 100) -> List[Dict]:
        """获取组织的仓库"""
        repos = []
        page = 1
        while True:
            data = self._make_request(
                f"{self.BASE_URL}/orgs/{org}/repos",
                params={"per_page": per_page, "page": page, "sort": "updated"}
            )
            if not data:
                break
            repos.extend(data)
            if len(data) < per_page:
                break
            page += 1
        return repos

    def get_all_repos_for_account(self, organizations: List[str]) -> List[Dict]:
        """获取账号下所有仓库（用户+组织）"""
        all_repos = []
        all_repos.extend(self.get_user_repos())
        for org in organizations:
            all_repos.extend(self.get_org_repos(org))
        return all_repos

    def validate_token(self) -> bool:
        """验证 Token 是否有效"""
        try:
            self._make_request(f"{self.BASE_URL}/user")
            return True
        except:
            return False