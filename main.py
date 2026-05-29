# -*- coding: utf-8 -*-
import os
import json
import webbrowser
import threading
import hashlib
from pathlib import Path
import sys
import logging

# 配置日志到文件
log_dir = Path(os.environ.get('APPDATA', '')) / "FlowLauncher" / "Logs" if os.environ.get('APPDATA') else None
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "github-quick-access.log", encoding="utf-8") if log_dir else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# 设置 stdout 为 UTF-8
if sys.stdout is None:
    pass
else:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 插件根目录
plugin_root = Path(__file__).parent.resolve()

def _get_settings_path():
    """获取 settings.json 路径，兼容 Flow Launcher 的插件配置目录"""
    # 尝试 Flow Launcher 全局插件配置目录
    appdata = os.environ.get('APPDATA', '')
    if appdata:
        # C:\Users\<user>\AppData\Roaming\FlowLauncher\Settings\Plugins\GitHub Quick Access
        settings_path = Path(appdata) / "FlowLauncher" / "Settings" / "Plugins" / "GitHub Quick Access" / "settings.json"
        if settings_path.exists():
            return settings_path
    # 回退到插件目录
    return plugin_root / "settings.json"

from github_client import GitHubClient
from cache_manager import CacheManager
from chrome_profile import ChromeProfileManager

ICON_PATH = "assets/favicon.ico"


class Main:
    """GitHub Quick Access 插件主类"""

    def __init__(self, rpc_settings=None):
        self.cache_manager = CacheManager()
        self.chrome_manager = ChromeProfileManager()
        self._settings = self._load_settings(rpc_settings)

    def _load_settings(self, rpc_settings=None):
        # 优先使用 Flow Launcher 传递的 settings
        if rpc_settings:
            settings = dict(rpc_settings)
            settings["cache_ttl_minutes"] = int(settings.get("cache_ttl_minutes") or 30)
            settings["max_results"] = int(settings.get("max_results") or 20)
            return settings
        # 回退到文件
        settings_path = _get_settings_path()
        if settings_path.exists():
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    settings["cache_ttl_minutes"] = int(settings.get("cache_ttl_minutes") or 30)
                    settings["max_results"] = int(settings.get("max_results") or 20)
                    return settings
            except Exception:
                pass
        return {"cache_ttl_minutes": 30, "max_results": 20, "accounts_json": "[]"}

    @property
    def settings(self):
        return self._settings

    def _get_accounts(self):
        """从 accounts_json 解析账号列表"""
        accounts_json = self.settings.get("accounts_json", "[]")
        try:
            accounts = json.loads(accounts_json)
        except json.JSONDecodeError:
            return []

        # 确保每个账号有稳定的 id（基于 token 生成）
        for acc in accounts:
            if "id" not in acc:
                token = acc.get("token", "")
                acc["id"] = hashlib.md5(token.encode()).hexdigest()[:8]

        return accounts

    def query(self, param: str):
        results = []
        q = param.strip()

        if not q:
            return [{
                "Title": "GitHub Quick Access",
                "SubTitle": "输入关键词搜索仓库，输入 gh help 查看帮助",
                "IcoPath": ICON_PATH,
            }]

        if q.lower() == "help":
            return [
                {"Title": "gh <关键词>", "SubTitle": "搜索仓库", "IcoPath": ICON_PATH},
                {"Title": "gh refresh", "SubTitle": "刷新所有账号的仓库缓存", "IcoPath": ICON_PATH},
                {"Title": "gh help", "SubTitle": "显示帮助", "IcoPath": ICON_PATH},
            ]

        if q.lower() == "refresh":
            for account in self._get_accounts():
                self._refresh_account_cache(account)
            return [{"Title": "刷新完成", "SubTitle": "所有账号的仓库缓存已更新", "IcoPath": ICON_PATH}]

        # 完整仓库名搜索: owner/repo 格式 → 显示 4 个页面选项
        if "/" in q:
            # 尝试提取 owner/repo（支持带后缀情况，如 "owner/repo 主页"）
            parts = q.split("/")
            if len(parts) >= 2:
                owner = parts[0].strip()
                # repo_name 是 / 后面的所有内容
                repo_name = "/".join(parts[1:]).strip()
                # 去掉可能的后缀文字
                for suffix in [" 主页", " MR", " Actions", " Issues"]:
                    if repo_name.endswith(suffix):
                        repo_name = repo_name[:-len(suffix)].strip()
                        break

                for account in self._get_accounts():
                    token = account.get("token", "")
                    if not token:
                        continue
                    cache = self.cache_manager.get_cache(account["id"], self.settings.get("cache_ttl_minutes", 30))
                    if not cache:
                        continue
                    for repo in cache.get("repositories", []):
                        full_name = repo.get("full_name", "")
                        if full_name.lower() == f"{owner}/{repo_name}".lower():
                            account_alias = account.get("alias", "unknown")
                            private_label = "私有仓库" if repo.get("is_private") else "公开仓库"
                            return [
                                {
                                    "Title": f"gh ▶ {full_name} 主页",
                                    "SubTitle": f"{private_label} | {account_alias}",
                                    "IcoPath": ICON_PATH,
                                    "JsonRPCAction": {
                                        "method": "openUrl",
                                        "parameters": [account["id"], full_name, "home"]
                                    }
                                },
                                {
                                    "Title": f"gh 🔀 {full_name} MR",
                                    "SubTitle": f"{private_label} | {account_alias}",
                                    "IcoPath": ICON_PATH,
                                    "JsonRPCAction": {
                                        "method": "openUrl",
                                        "parameters": [account["id"], full_name, "mr"]
                                    }
                                },
                                {
                                    "Title": f"gh ⚡ {full_name} Actions",
                                    "SubTitle": f"{private_label} | {account_alias}",
                                    "IcoPath": ICON_PATH,
                                    "JsonRPCAction": {
                                        "method": "openUrl",
                                        "parameters": [account["id"], full_name, "actions"]
                                    }
                                },
                                {
                                    "Title": f"gh 📋 {full_name} Issues",
                                    "SubTitle": f"{private_label} | {account_alias}",
                                    "IcoPath": ICON_PATH,
                                    "JsonRPCAction": {
                                        "method": "openUrl",
                                        "parameters": [account["id"], full_name, "issues"]
                                    }
                                },
                            ]

        results = []
        keyword_lower = q.lower()

        results = []
        keyword_lower = q.lower()

        for account in self._get_accounts():
            token = account.get("token", "")
            if not token:
                results.append({
                    "Title": f"[{account.get('alias', 'unknown')}] Token 未配置",
                    "SubTitle": "请在设置中添加 Token",
                    "IcoPath": ICON_PATH,
                })
                continue

            cache = self.cache_manager.get_cache(account["id"], self.settings.get("cache_ttl_minutes", 30))
            if not cache:
                results.append({
                    "Title": f"[{account.get('alias', 'unknown')}] 缓存为空",
                    "SubTitle": "输入 gh refresh 更新仓库列表",
                    "IcoPath": ICON_PATH,
                })
                continue

            for repo in cache.get("repositories", []):
                full_name = repo.get("full_name", "").lower()
                if keyword_lower in full_name:
                    account_alias = account.get("alias", "unknown")
                    repo_full_name = repo.get("full_name", "")
                    private_label = "私有仓库" if repo.get("is_private") else "公开仓库"
                    results.append({
                        "Title": f"{repo_full_name}",
                        "SubTitle": f"{private_label} | {account_alias} | 回车选择页面",
                        "IcoPath": ICON_PATH,
                        "JsonRPCAction": {
                            "method": "selectRepo",
                            "parameters": [account["id"], repo_full_name]
                        }
                    })

        # 如果只有一个精确匹配的结果，自动显示页面选项
        if len(results) == 1 and "/" in q:
            exact_match = results[0]
            repo_title = exact_match.get("Title", "")
            if repo_title.lower() == q.lower():
                # 精确匹配单个仓库，显示页面选项
                return self.query(repo_title)

        return results[:self.settings.get("max_results", 20)]

    def _refresh_account_cache(self, account):
        def _do_refresh():
            token = account.get("token", "")
            if not token:
                return
            try:
                client = GitHubClient(token)
                # 自动获取 organizations
                orgs_data = client.get_user_orgs()
                orgs = [org.get("login", "") for org in orgs_data]
                # 获取用户仓库 + 组织仓库
                repos = client.get_all_repos_for_account(orgs)
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
        account = next((a for a in self._get_accounts() if a.get("id") == account_id), None)
        if not account:
            return

        url = self.chrome_manager.build_url(repo_full_name, page)
        logger.debug(f"Opening URL: {url} for account_id: {account_id}, page: {page}")
        profile_path = account.get("chrome_profile_path", "")
        try:
            self.chrome_manager.open_url(profile_path, url)
        except Exception:
            webbrowser.open(url)

    def selectRepo(self, account_id: str, repo_full_name: str):
        """JSON-RPC action: 选择仓库后显示 4 个页面选项"""
        account = next((a for a in self._get_accounts() if a.get("id") == account_id), None)
        if not account:
            return []

        # 找到仓库信息
        cache = self.cache_manager.get_cache(account_id, self.settings.get("cache_ttl_minutes", 30))
        if not cache:
            return []
        private_label = "私有仓库"
        for repo in cache.get("repositories", []):
            if repo.get("full_name") == repo_full_name:
                private_label = "私有仓库" if repo.get("is_private") else "公开仓库"
                break

        account_alias = account.get("alias", "unknown")
        return [
            {
                "Title": f"gh ▶ {repo_full_name} 主页",
                "SubTitle": f"{private_label} | {account_alias}",
                "IcoPath": ICON_PATH,
                "JsonRPCAction": {
                    "method": "openUrl",
                    "parameters": [account_id, repo_full_name, "home"]
                }
            },
            {
                "Title": f"gh 🔀 {repo_full_name} MR",
                "SubTitle": f"{private_label} | {account_alias}",
                "IcoPath": ICON_PATH,
                "JsonRPCAction": {
                    "method": "openUrl",
                    "parameters": [account_id, repo_full_name, "mr"]
                }
            },
            {
                "Title": f"gh ⚡ {repo_full_name} Actions",
                "SubTitle": f"{private_label} | {account_alias}",
                "IcoPath": ICON_PATH,
                "JsonRPCAction": {
                    "method": "openUrl",
                    "parameters": [account_id, repo_full_name, "actions"]
                }
            },
            {
                "Title": f"gh 📋 {repo_full_name} Issues",
                "SubTitle": f"{private_label} | {account_alias}",
                "IcoPath": ICON_PATH,
                "JsonRPCAction": {
                    "method": "openUrl",
                    "parameters": [account_id, repo_full_name, "issues"]
                }
            },
        ]


def json_rpc_response(results: list, request_id=None) -> str:
    """生成 JSON-RPC 响应"""
    response = {"result": results}
    if request_id is not None:
        response["id"] = request_id
    return json.dumps(response, ensure_ascii=False)


def json_rpc_error(error_message: str, request_id=None) -> str:
    """生成 JSON-RPC 错误响应"""
    response = {"error": {"code": -32603, "message": error_message}}
    if request_id is not None:
        response["id"] = request_id
    return json.dumps(response, ensure_ascii=False)


def main():
    """插件入口 - 从 stdin 读取 JSON-RPC 请求，输出到 stdout"""
    try:
        # 从 stdin 读取请求
        request = sys.stdin.read() if sys.stdin else ""
        logger.debug(f"stdin request: '{request[:200]}...' " if len(request) > 200 else f"stdin request: '{request}'")
        request_id = None  # 初始化 request_id
        if not request:
            # 尝试从命令行参数读取
            if len(sys.argv) > 1:
                request = sys.argv[1]
                logger.debug(f"Using argv[1]: '{request}'")
            else:
                logger.debug("No input, returning empty")
                print(json_rpc_response([]))
                return

        # 解析请求
        try:
            req_data = json.loads(request)
            logger.debug(f"Parsed JSON, keys: {list(req_data.keys())}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            print(json_rpc_error("Invalid JSON"))
            return

        # Flow Launcher JSON-RPC 格式: {"method":"query","parameters":[search_term],"settings":{...},"id":0}
        method = req_data.get("method", "")
        params = req_data.get("parameters", [])
        request_id = req_data.get("id")
        logger.debug(f"Method: {method}, params: {params}, id: {request_id}")

        if method == "query" and len(params) >= 1:
            # 查询请求，搜索参数在 parameters[0]
            param = params[0] if params[0] else ""
            logger.debug(f"Query search param: '{param}'")
            rpc_settings = req_data.get("settings", {})
            logger.debug(f"RPC settings: {list(rpc_settings.keys())}")
            plugin = Main(rpc_settings=rpc_settings)
            results = plugin.query(param)
            logger.debug(f"Query returning {len(results)} results")
            response = json_rpc_response(results, request_id)
            logger.info(f"Query response: {response[:500]}...")
            print(response)
        elif method == "openUrl" and len(params) >= 3:
            # 打开 URL action
            rpc_settings = req_data.get("settings", {})
            plugin = Main(rpc_settings=rpc_settings)
            plugin.openUrl(params[0], params[1], params[2])
            print(json_rpc_response([{"type": "ok"}], request_id))
        elif method == "selectRepo" and len(params) >= 2:
            # 选择仓库 action - 打印调试日志
            logger.debug(f"selectRepo called with params: {params}")
            rpc_settings = req_data.get("settings", {})
            plugin = Main(rpc_settings=rpc_settings)
            results = plugin.selectRepo(params[0], params[1])
            logger.debug(f"selectRepo returning {len(results)} results")
            response = json_rpc_response(results, request_id)
            logger.info(f"selectRepo response: {response[:500]}...")
            print(response)
        else:
            print(json_rpc_response([], request_id))

    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
        print(json_rpc_error(str(e), request_id))


if __name__ == "__main__":
    main()
