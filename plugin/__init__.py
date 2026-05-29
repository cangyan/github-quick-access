# -*- coding: utf-8 -*-
"""
Flow Launcher Plugin: GitHub Quick Access
处理 JSON-RPC 通信协议
"""
import sys
import json

# 插件根目录
from pathlib import Path
plugin_root = Path(__file__).parent.parent


class FlowLauncherPlugin:
    """Flow Launcher JSON-RPC 协议处理基类"""

    def query(self, param: str):
        """处理查询请求 - 子类实现"""
        raise NotImplementedError

    def openUrl(self, account_id: str, repo_full_name: str, page: str):
        """打开 URL - JSON-RPC action"""
        pass


def json_rpc_response(results: list) -> str:
    """生成 JSON-RPC 响应"""
    return json.dumps({
        "result": results
    }, ensure_ascii=False)


def json_rpc_error(error: str) -> str:
    """生成 JSON-RPC 错误响应"""
    return json.dumps({
        "error": error
    }, ensure_ascii=False)


def main():
    """插件入口 - 从 stdin 读取 JSON-RPC 请求，输出到 stdout"""
    from plugin.ui import Main

    plugin = Main()

    try:
        # 从 stdin 读取请求
        request = sys.stdin.read()
        if not request:
            print(json_rpc_response([]))
            return

        # 解析请求
        try:
            req_data = json.loads(request)
        except json.JSONDecodeError:
            print(json_rpc_error("Invalid JSON"))
            return

        # 处理请求类型
        if "action" in req_data:
            # Action 请求 (JSON-RPC action)
            method = req_data.get("action", {}).get("method", "")
            params = req_data.get("action", {}).get("parameters", [])

            if method == "openUrl" and len(params) >= 3:
                plugin.openUrl(params[0], params[1], params[2])
                print(json_rpc_response([{"type": "ok"}]))
            else:
                print(json_rpc_response([]))
        else:
            # 查询请求
            param = req_data.get("search", "")
            results = plugin.query(param)
            print(json_rpc_response(results))

    except Exception as e:
        print(json_rpc_error(str(e)))


if __name__ == "__main__":
    main()