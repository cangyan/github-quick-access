# -*- coding: utf-8 -*-
import keyring
from typing import Optional

class KeyringManager:
    SERVICE_NAME = "FlowLauncher.Plugin.GitHubQuickAccess"

    def store_token(self, token_ref: str, token: str):
        """存储 Token 到系统密钥链"""
        keyring.set_password(self.SERVICE_NAME, token_ref, token)

    def get_token(self, token_ref: str) -> Optional[str]:
        """从系统密钥链获取 Token"""
        return keyring.get_password(self.SERVICE_NAME, token_ref)

    def delete_token(self, token_ref: str):
        """从系统密钥链删除 Token"""
        keyring.delete_password(self.SERVICE_NAME, token_ref)