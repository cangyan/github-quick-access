# -*- coding: utf-8 -*-


import os
from pathlib import Path

setting_pyfile = Path(__file__).resolve()
pludir = setting_pyfile.parent
basedir = pludir.parent


# the information of package
__package_name__ = "GitHubQuickAccess"
__version__ = "1.0.0"
__short_description__ = "多 GitHub 账号快速访问，支持 Chrome Profile 隔离"
GITHUB_USERNAME = "cangyan"


readme_path = basedir / "README.md"
try:
    __long_description__ = open(readme_path, "r").read()
except:
    __long_description__ = __short_description__


# extensions
TRANSLATIONS_PATH = basedir / "plugin/translations"

# plugin.json
PLUGIN_ID = "8c3b4d7e-5f6a-4b8c-9d1e-2f3a4b5c6d7e"  # could generate via python `uuid` official package
ICON_PATH = "assets/favicon.ico"
PLUGIN_AUTHOR = "Your Name"
PLUGIN_ACTION_KEYWORD = "gh"
PLUGIN_PROGRAM_LANG = "python"
PLUGIN_EXECUTE_FILENAME = "main.py"
PLUGIN_ZIP_NAME = f"{__package_name__}-{__version__}.zip"
PLUGIN_URL = f"https://github.com/{GITHUB_USERNAME}/{__package_name__}"
PLUGIN_URL_SOURCE_CODE = f"https://github.com/{GITHUB_USERNAME}/{__package_name__}"
PLUGIN_URL_DOWNLOAD = (
    f"{PLUGIN_URL_SOURCE_CODE}/releases/download/v{__version__}/{PLUGIN_ZIP_NAME}"
)
