# Flow.Launcher.Plugin.GitHubQuickAccess

多 GitHub 账号快速访问插件，支持 Chrome Profile 隔离。

## 功能

- **多账号管理**：支持添加多个 GitHub 账号
- **组织支持**：每个账号可关联多个 Organization
- **快速跳转**：输入 `gh <关键词>` 搜索仓库，一键打开：
  - 仓库主页
  - Merge Requests
  - Actions
  - Issues
- **Chrome Profile 隔离**：每个 GitHub 账号对应独立 Chrome Profile，免切换
- **本地缓存**：仓库列表本地缓存，搜索无延迟
- **安全存储**：Token 通过系统密钥链存储，不落盘

## 安装

1. 下载插件到 Flow Launcher 插件目录
2. 重启 Flow Launcher
3. 在插件设置中添加 GitHub 账号和 Chrome Profile

## 配置

首次使用需要配置：

1. **生成 GitHub Personal Access Token**
   - 访问 https://github.com/settings/tokens
   - 生成 classic token
   - 需要 `repo` 和 `read:user` 权限

2. **添加账号**
   - 插件会调用系统密钥链存储 Token
   - 配置 Chrome Profile 路径
   - 添加所属 Organization（如有）

3. **Chrome Profile 创建**
   - 打开 Chrome 设置 → 添加性能/配置文件
   - 或在 `chrome://settings/` 创建新配置文件
   - 登录对应的 GitHub 账号

## 使用方法

```
gh <关键词>   - 搜索仓库
gh refresh    - 刷新所有账号的仓库缓存
gh help       - 显示帮助
```

搜索结果示例：
```
▶ [Personal] owner/repo           - 打开主页
🔀 [Personal] owner/repo - MR    - 打开 Merge Requests
⚡ [Personal] owner/repo - Actions - 打开 Actions
📋 [Personal] owner/repo - Issues  - 打开 Issues
```

## 开发

```bash
# 安装依赖
pip install -r requirements.txt

# 本地调试（模拟 Flow Launcher 查询）
python main.py

# 运行测试
python -m pytest test/ -v
```

## 目录结构

```
.
├── github_client.py       # GitHub API 客户端
├── keyring_manager.py     # Token 系统密钥链存取
├── chrome_profile.py      # Chrome Profile 检测 + 打开
├── cache_manager.py       # 仓库缓存管理
├── settings_manager.py    # 账号配置管理
├── plugin/
│   ├── __init__.py        # 插件入口
│   ├── ui.py              # 查询逻辑 + JSON-RPC
│   ├── settings.py        # 插件元数据
│   └── translations/      # 国际化
├── test/                  # 测试
└── requirements.txt
```

## 技术栈

- Python 3
- Flow Launcher Plugin API
- GitHub REST API
- 系统密钥链（keyring）

## License

MIT