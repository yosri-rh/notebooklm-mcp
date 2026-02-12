# NotebookLM MCP Server

Connect Claude Code to Google NotebookLM using browser automation.

🖥️ **Claude Code Integration** | 🤖 **Browser Automation** | 📚 **NotebookLM Tools**

## ⚠️ Important Notes

- **No Official API**: This uses browser automation and may break with UI changes
- **Terms of Service**: May violate NotebookLM ToS; for personal/educational use only
- **Authentication Required**: Requires Google account with NotebookLM access
- **Maintenance Required**: UI selectors need updates when NotebookLM changes

## Why Browser Automation (Playwright + Chromium)?

### No Public API Available

NotebookLM (free version at https://notebooklm.google.com) provides no programmatic access:
- ❌ No REST API
- ❌ No Python SDK
- ❌ No webhooks or integrations

**The only interface is the web UI**, which requires browser automation.

### Technical Requirements

NotebookLM is a JavaScript single-page application (SPA). To automate it, we need:

1. **JavaScript execution** - The UI renders dynamically via JavaScript
2. **DOM manipulation** - Click buttons, fill forms, extract data
3. **Google OAuth** - Authenticate with Google account
4. **Session management** - Maintain cookies and authentication state

**Simple HTTP clients cannot work** because:
- Without JavaScript execution, you get empty HTML: `<div id="root"></div>`
- No access to rendered DOM elements
- Cannot handle OAuth authentication flow

### Why Playwright + Chromium?

**Playwright** is the best browser automation tool for Python:
- Modern async API with auto-waiting
- Python-native support
- Multi-architecture (ARM64/AMD64)
- Active development

**Chromium** is required as the browser engine:
- Executes JavaScript and renders UI
- Handles Google authentication
- Provides full browser capabilities

### Alternative: NotebookLM Enterprise API

Google offers **NotebookLM Enterprise** with an official API, but it:
- Requires Google Cloud project and enterprise licensing
- Only works with enterprise version, not free NotebookLM
- API is in alpha (v1alpha)

**This project targets free NotebookLM** to remain accessible without enterprise requirements.

Reference: [NotebookLM Enterprise API Docs](https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks)

## 🚀 Quick Start

```bash
# 1. Install dependencies
uv sync
uv run playwright install chromium

# 2. Authenticate with Google
uv run python scripts/setup_auth.py

# 3. The .mcp.json file is already configured
# Just use Claude Code and start interacting with NotebookLM!
```

### Example Usage in Claude Code

Once configured, try these prompts in Claude Code:

**Create and populate a notebook:**
```
Create a new NotebookLM notebook called "AI Research" and add these sources:
- https://arxiv.org/abs/2301.00001
- https://www.youtube.com/watch?v=example
```

**Query your notebooks:**
```
List all my NotebookLM notebooks, then query the "AI Research" notebook about
the main findings and create a summary.
```

**Generate study materials:**
```
For my "Course Notes" notebook, generate a FAQ study guide and then
generate an audio overview.
```

**Organize sources:**
```
Show me all sources in my "Research Papers" notebook and tell me
which ones are YouTube videos vs websites.
```

## Testing the MCP Server

Test the server with MCP Inspector before using with Claude Code:

```bash
# Install and run MCP Inspector
npx @modelcontextprotocol/inspector uv --directory /path/to/notebooklm-mcp run notebooklm-mcp

# Opens web interface at http://localhost:5173
# Try calling tools like list_notebooks(), create_notebook(), etc.
```

**Watch browser automation (debugging):**
```bash
# Run with visible browser to see what's happening
NOTEBOOKLM_HEADLESS=false uv run notebooklm-mcp
```

## Features

### Phase 1 - Essential Operations
- ✅ List all notebooks
- ✅ Create new notebook
- ✅ Add sources (website, YouTube, text)
- ✅ Query notebook with AI

### Phase 2 - Advanced Features
- ✅ Generate study guides (FAQ, briefing doc, table of contents)
- ✅ Generate audio overview (podcast)
- ✅ Get notebook sources

## Installation

```bash
cd /path/to/notebooklm-mcp

# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium
```

## Authentication Setup

Run this once to authenticate with your Google account:

```bash
uv run python scripts/setup_auth.py
```

This opens a browser where you:
1. Sign in to your Google account
2. Navigate to https://notebooklm.google.com
3. Verify access, then press Enter

Your session is saved to `chrome-user-data/` (gitignored).

## Configuration

### Environment Variables (Optional)

You can configure the MCP server using environment variables. There are two ways to set them:

#### Option 1: Set Directly in Terminal (Quick Testing)

```bash
# Run with custom settings
NOTEBOOKLM_HEADLESS=false LOG_LEVEL=DEBUG uv run notebooklm-mcp
```

#### Option 2: Use .env File (Persistent Configuration)

Create a `.env` file **in the project root directory** (next to `README.md`):

```bash
# From the project root directory
cd /path/to/notebooklm-mcp
cp .env.example .env
```

Edit `.env` with your preferred settings:

```bash
# Example .env file content
NOTEBOOKLM_HEADLESS=true
LOG_LEVEL=INFO
```

The `.env` file is automatically loaded when you run the server.

**File Location:**
```
notebooklm-mcp/
├── .env          # Your configuration file (create this)
├── .env.example  # Template (already exists)
├── README.md
├── pyproject.toml
└── ...
```

#### Available Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTEBOOKLM_HEADLESS` | `true` | Run browser in headless mode. Set to `false` to see browser (useful for debugging) |
| `LOG_LEVEL` | `INFO` | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

**Note:** For Claude Code usage, you typically don't need a `.env` file - the default settings work fine. The `.env` file is mainly useful for debugging.

## Claude Code Integration

The `.mcp.json` file in the project root configures the MCP server:

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/notebooklm-mcp",
        "run",
        "notebooklm-mcp"
      ],
      "env": {
        "NOTEBOOKLM_HEADLESS": "true"
      }
    }
  }
}
```

**Important:** Update the `--directory` path to match your actual project location.

Once configured, Claude Code will automatically load the MCP server when you work in this directory.

## Testing

### With MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/notebooklm-mcp run notebooklm-mcp
```

### Watch Browser Automation

```bash
NOTEBOOKLM_HEADLESS=false uv run notebooklm-mcp
```

### In Claude Code

Try these prompts:
- "List my NotebookLM notebooks"
- "Create a notebook called 'Test'"
- "Add https://example.com to notebook [ID]"
- "Ask notebook [ID]: What are the main topics?"

## Available Tools

### `list_notebooks()`
List all available NotebookLM notebooks.

**Returns**: List of notebooks with id, title, and url

**Example Output**:
```json
[
  {
    "id": "abc123def456",
    "title": "Research Notes",
    "url": "https://notebooklm.google.com/notebook/abc123def456"
  }
]
```

### `create_notebook(name: str)`
Create a new NotebookLM notebook.

**Args**:
- `name`: Name for the notebook

**Returns**: Created notebook details

### `add_source(notebook_id: str, source_type: str, content: str)`
Add a source to a notebook.

**Args**:
- `notebook_id`: Notebook ID
- `source_type`: "website", "youtube", or "text"
- `content`: URL for website/youtube, or raw text

**Returns**: Status message

### `query_notebook(notebook_id: str, query: str)`
Ask NotebookLM's AI a question about the notebook's sources.

**Args**:
- `notebook_id`: Notebook ID
- `query`: Question to ask

**Returns**: AI-generated response as string

### `generate_study_guide(notebook_id: str, guide_type: str)`
Generate a study guide from notebook sources.

**Args**:
- `notebook_id`: Notebook ID
- `guide_type`: "faq", "briefing_doc", or "table_of_contents"

**Returns**: Status message

### `generate_audio_overview(notebook_id: str)`
Generate an audio overview (podcast) from notebook sources.

**Note**: This is an async operation in NotebookLM. Audio generation may take several minutes to complete.

**Args**:
- `notebook_id`: Notebook ID

**Returns**: Status message

### `get_notebook_sources(notebook_id: str)`
Get list of sources in a notebook.

**Args**:
- `notebook_id`: Notebook ID

**Returns**: List of sources with index and title

## Troubleshooting

### Common Issues

#### MCP server not showing in Claude Code

1. Check that `.mcp.json` exists in the project root
2. Verify JSON syntax is valid (no trailing commas)
3. Check the path in config points to your project directory
4. Restart Claude Code
5. Run `claude mcp list` to verify the server is registered

#### Authentication expired

```bash
# Re-run authentication setup
uv run python scripts/setup_auth.py

# Or delete chrome-user-data and start fresh
rm -rf chrome-user-data
uv run python scripts/setup_auth.py
```

#### Playwright/Chromium issues

```bash
# Reinstall Playwright browsers
uv run playwright install chromium --force
uv run playwright install-deps chromium

# On Linux, you may need system dependencies
sudo apt-get install -y \
  libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
  libxdamage1 libxfixes3 libxrandr2 libgbm1 \
  libpango-1.0-0 libcairo2 libasound2
```

#### UI selectors not working

NotebookLM UI may have changed. Inspect the UI in DevTools and update selectors in `src/notebooklm_mcp/selectors.py`.

#### Browser automation fails

```bash
# Run with visible browser to see what's happening
NOTEBOOKLM_HEADLESS=false uv run notebooklm-mcp

# Enable debug logging
LOG_LEVEL=DEBUG uv run notebooklm-mcp
```

#### Tools not responding in Claude Code

1. Check if MCP server is registered: `claude mcp list`
2. Try simple tool first: "List my NotebookLM notebooks"
3. Check for errors in the output
4. Restart Claude Code

## Project Structure

```
notebooklm-mcp/
├── src/notebooklm_mcp/
│   ├── __init__.py
│   ├── server.py       # FastMCP server with tool definitions
│   ├── browser.py      # Playwright browser manager
│   ├── selectors.py    # NotebookLM UI selectors
│   └── utils.py        # Helper functions
├── scripts/
│   └── setup_auth.py   # Interactive Google login
├── chrome-user-data/   # Persistent browser profile (gitignored)
├── .mcp.json          # Claude Code MCP server configuration
├── pyproject.toml
├── .env
└── README.md
```

## License

MIT License - Personal/Educational use only

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by Google. Use at your own risk.
