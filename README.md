# NotebookLM MCP Server

Connect Claude to Google NotebookLM using browser automation.

🐳 **Fully Containerized** | ☸️ **Kubernetes & OpenShift Ready** | 🔒 **Production Hardened**

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

### Container Size: 800MB-2GB

This is **normal** for browser automation containers:

```
Base Python 3.12:           ~150 MB
Chromium browser:           ~300 MB
System dependencies:        ~200 MB (X11, fonts, codecs)
Python packages:            ~150 MB (Playwright, FastMCP)
Application code:            ~5 MB
Total:                      800 MB - 2 GB
```

**Comparison with similar tools:**
- Selenium Chrome: ~1.2 GB
- Browserless: ~1.1 GB
- Playwright official: ~900 MB

### Alternative: NotebookLM Enterprise API

Google offers **NotebookLM Enterprise** with an official API, but it:
- Requires Google Cloud project and enterprise licensing
- Only works with enterprise version, not free NotebookLM
- API is in alpha (v1alpha)

**This project targets free NotebookLM** to remain accessible without enterprise requirements.

Reference: [NotebookLM Enterprise API Docs](https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks)

## 🚀 Deployment Options

- **Local Development**: Run with Podman or Python
- **Podman**: Containerized deployment
- **Kubernetes**: Helm chart for standard Kubernetes
- **OpenShift 4.19**: Optimized Helm chart with Routes, SCCs, and monitoring

See [CONTAINERIZATION_SUMMARY.md](CONTAINERIZATION_SUMMARY.md) and [OPENSHIFT_SUMMARY.md](OPENSHIFT_SUMMARY.md)

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

Create `.env` file (optional):

```bash
cp .env.example .env
```

Settings:
- `NOTEBOOKLM_HEADLESS=true` - Run browser headless (set to `false` for debugging)
- `LOG_LEVEL=INFO` - Logging level

## Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/notebooklm-mcp",
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

Restart Claude Desktop after adding configuration.

## Testing

### With MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/notebooklm-mcp run notebooklm-mcp
```

### Watch Browser Automation

```bash
NOTEBOOKLM_HEADLESS=false uv run notebooklm-mcp
```

### In Claude Desktop

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
  },
  {
    "id": "xyz789ghi012",
    "title": "Project Documentation",
    "url": "https://notebooklm.google.com/notebook/xyz789ghi012"
  }
]
```

### `create_notebook(name: str)`
Create a new NotebookLM notebook.

**Args**:
- `name`: Name for the notebook

**Returns**: Created notebook details

**Example Output**:
```json
{
  "id": "new123notebook",
  "title": "My New Notebook",
  "url": "https://notebooklm.google.com/notebook/new123notebook"
}
```

### `add_source(notebook_id: str, source_type: str, content: str)`
Add a source to a notebook.

**Args**:
- `notebook_id`: Notebook ID
- `source_type`: "website", "youtube", or "text"
- `content`: URL for website/youtube, or raw text

**Returns**: Status message

**Example Output**:
```json
{
  "status": "success",
  "message": "Added website source to notebook",
  "notebook_id": "abc123def456"
}
```

### `query_notebook(notebook_id: str, query: str)`
Ask NotebookLM's AI a question about the notebook's sources.

**Args**:
- `notebook_id`: Notebook ID
- `query`: Question to ask

**Returns**: AI-generated response as string

**Example Output**:
```
Based on the sources provided, the main topics covered include:

1. Machine Learning Fundamentals - including supervised and unsupervised learning
2. Neural Network Architectures - covering CNNs, RNNs, and Transformers
3. Training Best Practices - optimization techniques and regularization methods

The sources particularly emphasize the importance of data preprocessing and
model evaluation strategies.
```

### `generate_study_guide(notebook_id: str, guide_type: str)`
Generate a study guide from notebook sources.

**Args**:
- `notebook_id`: Notebook ID
- `guide_type`: "faq", "briefing_doc", or "table_of_contents"

**Returns**: Status message

**Example Output**:
```json
{
  "status": "success",
  "message": "Generated faq study guide",
  "notebook_id": "abc123def456",
  "guide_type": "faq"
}
```

### `generate_audio_overview(notebook_id: str)`
Generate an audio overview (podcast) from notebook sources.

**Note**: This is an async operation in NotebookLM. Audio generation may take several minutes to complete.

**Args**:
- `notebook_id`: Notebook ID

**Returns**: Status message

**Example Output**:
```json
{
  "status": "success",
  "message": "Audio overview generation started",
  "notebook_id": "abc123def456",
  "note": "Audio generation is async and may take several minutes"
}
```

### `get_notebook_sources(notebook_id: str)`
Get list of sources in a notebook.

**Args**:
- `notebook_id`: Notebook ID

**Returns**: List of sources with index and title

**Example Output**:
```json
[
  {
    "index": "1",
    "title": "Introduction to Machine Learning - Wikipedia"
  },
  {
    "index": "2",
    "title": "Neural Networks Explained - YouTube"
  },
  {
    "index": "3",
    "title": "Custom text notes on deep learning concepts"
  }
]
```

## Troubleshooting

### Authentication expired
```bash
uv run python scripts/setup_auth.py
```

### UI selectors not working
NotebookLM UI may have changed. Inspect the UI in DevTools and update selectors in `src/notebooklm_mcp/selectors.py`.

### Browser automation fails
Set `NOTEBOOKLM_HEADLESS=false` to watch browser and debug.

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
├── pyproject.toml
├── .env
└── README.md
```

## License

MIT License - Personal/Educational use only

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by Google. Use at your own risk.
