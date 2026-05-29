# -*- coding: utf-8 -*-
"""
Token storage using simple file-based approach.
Tokens are stored in settings.json alongside account configuration.
This works with Flow Launcher's embedded Python (no external dependencies).
"""
import json
import base64
from pathlib import Path
from typing import Optional


class KeyringManager:
    """
    Token storage manager.
    Tokens are stored in settings.json as base64-encoded strings.
    This avoids the need for external keyring dependencies.
    """

    def __init__(self, settings_path: str = None):
        if settings_path:
            self.settings_path = Path(settings_path)
        else:
            self.settings_path = Path(__file__).parent / "settings.json"

    def _load_settings(self) -> dict:
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_settings(self, data: dict):
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def store_token(self, token_ref: str, token: str):
        """存储 Token（base64 编码后存储）"""
        settings = self._load_settings()
        if "tokens" not in settings:
            settings["tokens"] = {}
        # Base64 encode to avoid JSON escaping issues
        settings["tokens"][token_ref] = base64.b64encode(token.encode()).decode()
        self._save_settings(settings)

    def get_token(self, token_ref: str) -> Optional[str]:
        """获取 Token（base64 解码）"""
        settings = self._load_settings()
        tokens = settings.get("tokens", {})
        encoded = tokens.get(token_ref)
        if encoded:
            try:
                return base64.b64decode(encoded.encode()).decode()
            except:
                return None
        return None

    def delete_token(self, token_ref: str):
        """删除 Token"""
        settings = self._load_settings()
        if "tokens" in settings and token_ref in settings["tokens"]:
            del settings["tokens"][token_ref]
            self._save_settings(settings)