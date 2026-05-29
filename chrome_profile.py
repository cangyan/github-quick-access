# -*- coding: utf-8 -*-
import os
import platform
import subprocess
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ChromeProfileManager:
    """Chrome Profile 自动检测和浏览器打开"""

    PROFILE_PATHS = {
        "windows": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data"),
        "darwin": os.path.expanduser("~/Library/Application Support/Google/Chrome"),
        "linux": os.path.expanduser("~/.config/google-chrome"),
    }

    def __init__(self):
        self.system = platform.system().lower()

    def get_chrome_executable(self) -> Optional[str]:
        """获取 Chrome 可执行文件路径"""
        if self.system == "windows":
            paths = [
                os.path.join(os.environ.get("ProgramFiles", ""), "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
            ]
        elif self.system == "darwin":
            paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
        else:
            paths = ["/usr/bin/google-chrome", "/usr/bin/chromium-browser"]
        for path in paths:
            if os.path.exists(path):
                return path
        return None

    def detect_profiles(self) -> List[Dict[str, str]]:
        """自动检测系统中的 Chrome Profile"""
        base_path = self.PROFILE_PATHS.get(self.system, "")
        if not base_path or not os.path.exists(base_path):
            return []

        profiles = []
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if item.startswith("Profile ") and os.path.isdir(item_path):
                profiles.append({"id": item, "name": item, "path": item_path})
            elif item == "Default" and os.path.isdir(item_path):
                profiles.append({"id": "Default", "name": "Default", "path": item_path})

        # 从 Local State 解析 Profile 名称
        local_state_path = os.path.join(base_path, "Local State")
        if os.path.exists(local_state_path):
            try:
                with open(local_state_path, "r", encoding="utf-8") as f:
                    local_state = json.load(f)
                    info_cache = local_state.get("profile", {}).get("info_cache", {})
                    for profile_id, info in info_cache.items():
                        for p in profiles:
                            if p["id"] == profile_id or (p["id"] == "Default" and profile_id == "Default"):
                                p["name"] = info.get("name", p["name"])
                                break
            except:
                pass
        return profiles

    def open_url(self, profile_path: str, url: str):
        """在指定 Chrome Profile 中打开 URL"""
        chrome = self.get_chrome_executable()
        if not chrome:
            raise Exception("Chrome executable not found")

        # 提取 profile 目录名称（去除路径，只保留 "Profile 1" 这样的名称）
        profile_dir = os.path.basename(profile_path)

        if self.system == "windows":
            cmd = [chrome, f"--profile-directory={profile_dir}", url]
        elif self.system == "darwin":
            cmd = ["open", "-a", chrome, f"--args --profile-directory={profile_dir}", url]
        else:
            cmd = [chrome, f"--profile-directory={profile_dir}", url]

        logger.debug(f"Running command: {' '.join(cmd)}")
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @staticmethod
    def build_url(repo_full_name: str, page: str) -> str:
        """构建 GitHub 页面 URL"""
        base = f"https://github.com/{repo_full_name}"
        if page == "home":
            return base
        elif page == "mr":
            return f"{base}/pulls"
        elif page == "actions":
            return f"{base}/actions"
        elif page == "issues":
            return f"{base}/issues"
        return base