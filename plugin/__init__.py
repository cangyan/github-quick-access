# -*- coding: utf-8 -*-
"""
Flow Launcher Plugin: GitHub Quick Access
处理 JSON-RPC 通信协议
"""
import sys
import json
import base64

# 插件根目录
from pathlib import Path
plugin_root = Path(__file__).parent.parent


def json_rpc_response(results: list) -> str:
    """生成 JSON-RPC 响应"""
    return json.dumps({
        "result": results
    }, ensure_ascii=False)


def json_rpc_error(error_message: str) -> str:
    """生成 JSON-RPC 错误响应"""
    return json.dumps({
        "error": {"code": -32603, "message": error_message}
    }, ensure_ascii=False)


def generate_settings_ui() -> str:
    """生成设置界面 HTML"""
    # 加载现有配置
    settings_path = plugin_root / "settings.json"
    accounts = []
    if settings_path.exists():
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                accounts = data.get("accounts", [])
        except:
            pass

    # 生成账号列表 HTML
    accounts_html = ""
    for acc in accounts:
        alias = acc.get("alias", "未命名")
        acc_id = acc.get("id", "")
        profile = acc.get("chrome_profile_path", "")
        orgs = ", ".join(acc.get("organizations", []))
        token_ref = acc.get("token_ref", "")
        accounts_html += f"""
        <div style="border:1px solid #ccc;padding:10px;margin:10px 0;border-radius:4px;">
            <h4 style="margin:0 0 10px 0;">账号: {alias}</h4>
            <p style="margin:5px 0;"><strong>ID:</strong> {acc_id}</p>
            <p style="margin:5px 0;"><strong>Token ref:</strong> {token_ref}</p>
            <p style="margin:5px 0;"><strong>Chrome Profile:</strong> {profile or "未配置"}</p>
            <p style="margin:5px 0;"><strong>Organizations:</strong> {orgs or "无"}</p>
            <button onclick="deleteAccount('{acc_id}')" style="background:#ff4444;color:white;border:none;padding:5px 10px;cursor:pointer;">删除</button>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GitHub Quick Access 设置</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto; }}
        h2 {{ color: #333; }}
        .form-group {{ margin-bottom: 15px; }}
        label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
        input[type="text"], input[type="password"] {{ width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }}
        button {{ background: #4CAF50; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 4px; }}
        button:hover {{ background: #45a049; }}
        .account-list {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h2>⚙️ GitHub Quick Access 设置</h2>

    <h3>添加账号</h3>
    <form id="addAccountForm">
        <div class="form-group">
            <label>账号别名 (如: Personal, Work):</label>
            <input type="text" id="alias" placeholder="Personal" required>
        </div>
        <div class="form-group">
            <label>GitHub Personal Access Token:</label>
            <input type="password" id="token" placeholder="ghp_xxxxxxxxxxxx" required>
        </div>
        <div class="form-group">
            <label>Chrome Profile 路径:</label>
            <input type="text" id="chromeProfile" placeholder="C:\\Users\\你的用户名\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1">
        </div>
        <div class="form-group">
            <label>Organizations (逗号分隔，可留空):</label>
            <input type="text" id="orgs" placeholder="org1, org2">
        </div>
        <button type="submit">添加账号</button>
    </form>

    <div class="account-list">
        <h3>已配置的账号</h3>
        {accounts_html if accounts_html else "<p>暂无账号</p>"}
    </div>

    <script>
        document.getElementById('addAccountForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            const alias = document.getElementById('alias').value;
            const token = document.getElementById('token').value;
            const chromeProfile = document.getElementById('chromeProfile').value;
            const orgs = document.getElementById('orgs').value.split(',').map(s => s.trim()).filter(s => s);
            const encodedToken = btoa(token);
            const result = FlowLauncher.SaveSettings(JSON.stringify({{
                action: 'add_account',
                alias: alias,
                token: encodedToken,
                chrome_profile_path: chromeProfile,
                organizations: orgs
            }}));
            if (result) {{
                location.reload();
            }}
        }});

        function deleteAccount(accId) {{
            if (confirm('确定要删除这个账号吗？')) {{
                const result = FlowLauncher.SaveSettings(JSON.stringify({{
                    action: 'delete_account',
                    account_id: accId
                }}));
                if (result) {{
                    location.reload();
                }}
            }}
        }}
    </script>
</body>
</html>
"""
    return base64.b64encode(html.encode('utf-8')).decode('utf-8')


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
        elif req_data.get("method") == "Settings":
            # Flow Launcher 请求设置界面
            ui_html = generate_settings_ui()
            print(json_rpc_response([{
                "Title": "GitHub Quick Access 设置",
                "SubTitle": "配置 GitHub 账号和 Chrome Profile",
                "IcoPath": "assets/favicon.ico",
                "JsonRPCAction": {
                    "method": "OpenSettings",
                    "parameters": [ui_html]
                }
            }]))
        else:
            # 查询请求
            param = req_data.get("search", "")
            results = plugin.query(param)
            print(json_rpc_response(results))

    except Exception as e:
        print(json_rpc_error(str(e)))


if __name__ == "__main__":
    main()