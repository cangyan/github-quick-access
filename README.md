# Flow.Launcher.Plugin.GitHubQuickAccess

Multi-GitHub account quick access plugin with Chrome Profile isolation.

## Features

- **Multi-account management**: Add multiple GitHub accounts, each with independent Token and Chrome Profile
- **Auto organization discovery**: Automatically fetch user's organizations via Token API, no manual config needed
- **Quick navigation**: Enter `gh <keyword>` to search repos, open with one click:
  - Repository Home
  - Merge Requests
  - Actions
  - Issues
- **Chrome Profile isolation**: Each GitHub account maps to a separate Chrome Profile, no switching needed
- **Local cache**: Repository list cached locally, search is instant
- **Multi-language**: Supports English, Chinese, Japanese (selectable in settings)

## Install

1. Download `GitHubQuickAccess-1.0.43.zip` and extract to Flow Launcher plugin directory
2. Restart Flow Launcher
3. Configure GitHub accounts in plugin settings

## Configuration

### 1. Generate GitHub Personal Access Token

Visit https://github.com/settings/tokens
- Generate a classic token
- Required scopes: `repo` and `read:user`

### 2. Configure Account

Add accounts in the plugin settings (Account config JSON):

```json
[
  {
    "alias": "Personal",
    "token": "ghp_xxxxxxxxxxxx",
    "chrome_profile_path": "C:\\Users\\YourUser\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1"
  },
  {
    "alias": "Work",
    "token": "ghp_yyyyyyyyyyyy",
    "chrome_profile_path": "C:\\Users\\YourUser\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2"
  }
]
```

### 3. UI Language

Set `language` in settings to: `en`, `zh`, or `ja` (default: `en`)

### 4. Chrome Profile Creation

- Open Chrome Settings → Add person/profile
- Or create new profile at `chrome://settings/`
- Log in to the corresponding GitHub account

## Usage

```
gh <keyword>   - Search repositories
gh refresh    - Refresh all accounts' repository cache
gh help       - Show help
```

### Interaction Flow

1. Enter `gh <keyword>` to search repos
2. Select a repo and press Enter → query changes to `gh owner/repo`
3. Shows 4 page options: Home, MR, Actions, Issues
4. Select a page option → opens corresponding GitHub page

### Search Results Example

```
# Search list (select repo + Enter)
owner/repo  Public repository | Personal | Press Enter to select page

# After selection, shows page options
owner/repo Home    - Open home page
owner/repo MR      - Open Merge Requests
owner/repo Actions - Open Actions
owner/repo Issues  - Open Issues
```

## Technical Highlights

- **Zero external dependencies**: Pure Python stdlib (urllib, json)
- **Embedded Python compatible**: Optimized for Flow Launcher's embedded Python environment
- **Native JSON-RPC**: Direct stdin/stdout communication with Flow Launcher

## Development

```bash
# Local debug
python main.py

# Run tests
python -m pytest test/ -v
```

## Directory Structure

```
.
├── github_client.py         # GitHub API client (urllib)
├── chrome_profile.py        # Chrome Profile detection + open
├── cache_manager.py         # Repository cache management
├── main.py                  # Plugin entry point
├── SettingsTemplate.yaml    # Settings UI template
├── plugin.json              # Plugin manifest
├── plugin/
│   ├── __init__.py          # JSON-RPC protocol handler
│   ├── ui.py                # Query logic
│   └── translations/        # i18n (en.json, zh.json, ja.json)
└── assets/                  # Icon resources
```

## License

MIT