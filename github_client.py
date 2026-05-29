# -*- coding: utf-8 -*-
import requests
from typing import List, Dict, Optional

class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        })

    def get_user_repos(self, per_page: int = 100) -> List[Dict]:
        """获取当前用户的仓库（包括私有）"""
        repos = []
        page = 1
        while True:
            resp = self.session.get(
                f"{self.BASE_URL}/user/repos",
                params={"per_page": per_page, "page": page, "sort": "updated"}
            )
            if resp.status_code != 200:
                raise Exception(f"GitHub API error: {resp.status_code} {resp.text}")
            data = resp.json()
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
            resp = self.session.get(
                f"{self.BASE_URL}/orgs/{org}/repos",
                params={"per_page": per_page, "page": page, "sort": "updated"}
            )
            if resp.status_code != 200:
                raise Exception(f"GitHub API error: {resp.status_code} {resp.text}")
            data = resp.json()
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
            resp = self.session.get(f"{self.BASE_URL}/user")
            return resp.status_code == 200
        except:
            return False