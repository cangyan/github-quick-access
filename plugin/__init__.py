# -*- coding: utf-8 -*-
"""
Flow Launcher Plugin: GitHub Quick Access
处理 JSON-RPC 通信协议
"""
import sys
import json
import base64
from pathlib import Path

# 插件根目录
plugin_root = Path(__file__).parent.parent

# --- i18n for settings UI ---
_settings_translations: dict = {}
_settings_locale: str = "en"

def _load_settings_translations():
    global _settings_translations
    trans_dir = plugin_root / "plugin" / "translations"
    for f in trans_dir.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            _settings_translations[f.stem] = json.load(fp)

def _t(key: str, locale: str = None) -> str:
    loc = locale or _settings_locale
    return _settings_translations.get(loc, {}).get(key, _settings_translations.get("en", {}).get(key, key))

def _detect_locale():
    """Detect language from settings.json"""
    settings_path = plugin_root / "settings.json"
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

# Load translations on import
_load_settings_translations()
_settings_locale = _detect_locale()


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
        alias = acc.get("alias", _t("unconfigured"))
        acc_id = acc.get("id", "")
        profile = acc.get("chrome_profile_path", "")
        orgs = ", ".join(acc.get("organizations", []))
        token_ref = acc.get("token_ref", "")
        accounts_html += f"""
        <div style="border:1px solid #ccc;padding:10px;margin:10px 0;border-radius:4px;">
            <h4 style="margin:0 0 10px 0;">{_t("plugin_name")}: {alias}</h4>
            <p style="margin:5px 0;"><strong>ID:</strong> {acc_id}</p>
            <p style="margin:5px 0;"><strong>Token ref:</strong> {token_ref or _t("unconfigured")}</p>
            <p style="margin:5px 0;"><strong>Chrome Profile:</strong> {profile or _t("unconfigured")}</p>
            <p style="margin:5px 0;"><strong>Organizations:</strong> {orgs or _t("none")}</p>
            <button onclick="deleteAccount('{acc_id}')" style="background:#ff4444;color:white;border:none;padding:5px 10px;cursor:pointer;">{_t("delete_account")}</button>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{_t("plugin_name")} {_t("settings_title")}</title>
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
    <h2>⚙️ {_t("settings_btn")}</h2>

    <h3>{_t("add_account")}</h3>
    <form id="addAccountForm">
        <div class="form-group">
            <label>{_t("account_alias_placeholder")}</label>
            <input type="text" id="alias" placeholder="Personal" required>
        </div>
        <div class="form-group">
            <label>GitHub Personal Access Token:</label>
            <input type="password" id="token" placeholder="ghp_xxxxxxxxxxxx" required>
        </div>
        <div class="form-group">
            <label>{_t("chrome_profile_path")}</label>
            <input type="text" id="chromeProfile" placeholder="C:\\Users\\...">
        </div>
        <div class="form-group">
            <label>{_t("orgs_placeholder")}</label>
            <input type="text" id="orgs" placeholder="org1, org2">
        </div>
        <button type="submit">{_t("add_account")}</button>
    </form>

    <div class="account-list">
        <h3>{_t("configured_accounts")}</h3>
        {accounts_html if accounts_html else f"<p>{_t('no_accounts')}</p>"}
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
            if (confirm('{_t("delete_confirm")}')) {{
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
            # Flow Launcher 请求设置界面 - 返回内置设置结果
            # 让 Flow Launcher 显示内置设置面板
            settings_path = plugin_root / "settings.json"
            settings_content = ""
            if settings_path.exists():
                try:
                    with open(settings_path, "r", encoding="utf-8") as f:
                        settings_content = f.read()
                except:
                    settings_content = "{}"
            else:
                settings_content = '{"accounts": [], "cache_ttl_minutes": 30, "max_results": 20}'

            print(json_rpc_response([{
                "Title": f"⚙️ {_t('settings_btn')}",
                "SubTitle": _t("settings_hint"),
                "IcoPath": "assets/favicon.ico",
                "JsonRPCAction": {
                    "method": "OpenSettings",
                    "parameters": [settings_content]
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