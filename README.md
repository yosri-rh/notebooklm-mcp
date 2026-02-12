# NotebookLM MCP Server

Connect Claude Desktop to Google NotebookLM using browser automation.

🖥️ **Local Development First** | 🐳 **Container Support** | 🧪 **Kubernetes/OpenShift Experimental**

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

### Primary Use Case: Local Development

This MCP server is **designed for local use with Claude Desktop**:

- ✅ **Python (Recommended)**: Direct integration with Claude Desktop via stdio
- ✅ **Podman Local**: Containerized testing on your local machine

### Experimental: Containerized Deployments

⚠️ **Multi-user deployments on Kubernetes/OpenShift are experimental** due to authentication challenges:

- Each user needs their own Google account session
- No official NotebookLM API for programmatic authentication
- Browser automation (Playwright) is designed for single-user scenarios
- Significant complexity for session isolation and management

**Available for reference/experimentation:**
- 🐳 **Podman**: Single-user containerized deployment
- ☸️ **Kubernetes**: Helm chart (experimental, single-user per pod)
- 🔴 **OpenShift**: Helm chart with Routes and SCCs (experimental, single-user per pod)

See [CONTAINERIZATION_SUMMARY.md](docs/CONTAINERIZATION_SUMMARY.md) and [OPENSHIFT_SUMMARY.md](docs/OPENSHIFT_SUMMARY.md) for experimental deployment guides.

## Quick Start (Local Development)

```bash
# 1. Install dependencies
uv sync
uv run playwright install chromium

# 2. Authenticate with Google
uv run python scripts/setup_auth.py

# 3. Configure Claude Desktop
# Add to ~/Library/Application Support/Claude/claude_desktop_config.json
# See "Claude Desktop Integration" section below

# 4. Restart Claude Desktop and start using NotebookLM tools!
```

### Example Usage in Claude Desktop

Once configured, try these prompts in Claude Desktop:

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

### Testing the MCP Server

Test the server with MCP Inspector before using with Claude Desktop:

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
| `MCP_TRANSPORT` | `stdio` | Transport mode: `stdio` (Claude Desktop) or `streamable-http` (containers) |
| `MCP_HOST` | `0.0.0.0` | HTTP bind address (only for `streamable-http` mode) |
| `MCP_PORT` | `8080` | HTTP port (only for `streamable-http` mode) |

**Note:** For Claude Desktop usage, you typically don't need a `.env` file - the default settings work fine. The `.env` file is mainly useful for debugging or container deployments.

## Local Podman Deployment

For containerized local testing without Kubernetes complexity:

### Using Podman Compose (Recommended)

```bash
# Clone and navigate to project
git clone https://github.com/yosri-rh/notebooklm-mcp.git
cd notebooklm-mcp

# Start the container
podman-compose up -d

# View logs
podman-compose logs -f

# Authenticate with Google (required once)
podman exec -it notebooklm-mcp uv run python scripts/setup_auth.py

# Stop the container
podman-compose down
```

### Manual Podman Commands

```bash
# Build the image
podman build -t notebooklm-mcp:latest -f Containerfile .

# Create a volume for authentication data
podman volume create notebooklm-chrome-data

# Run the container (stdio mode for local use)
podman run -d \
  --name notebooklm-mcp \
  --restart unless-stopped \
  -e NOTEBOOKLM_HEADLESS=true \
  -e LOG_LEVEL=INFO \
  -v notebooklm-chrome-data:/app/chrome-user-data \
  notebooklm-mcp:latest

# Authenticate with Google
podman exec -it notebooklm-mcp uv run python scripts/setup_auth.py

# View logs
podman logs -f notebooklm-mcp

# Stop and remove
podman stop notebooklm-mcp
podman rm notebooklm-mcp
```

### Testing HTTP Mode Locally

```bash
# Run in HTTP mode for testing
podman run -d \
  --name notebooklm-mcp-http \
  -p 8080:8080 \
  -e MCP_TRANSPORT=streamable-http \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8080 \
  -e NOTEBOOKLM_HEADLESS=true \
  -v notebooklm-chrome-data:/app/chrome-user-data \
  notebooklm-mcp:latest

# Test health endpoint
curl http://localhost:8080/health

# Connect with MCP Inspector
npx @modelcontextprotocol/inspector http://localhost:8080/mcp
```

## Local Podman Deployment

For containerized local testing without Kubernetes complexity:

### Using Podman Compose (Recommended)

```bash
# Clone and navigate to project
git clone https://github.com/yosri-rh/notebooklm-mcp.git
cd notebooklm-mcp

# Start the container
podman-compose up -d

# View logs
podman-compose logs -f

# Authenticate with Google (required once)
podman exec -it notebooklm-mcp uv run python scripts/setup_auth.py

# Stop the container
podman-compose down
```

### Manual Podman Commands

```bash
# Build the image
podman build -t notebooklm-mcp:latest -f Containerfile .

# Create a volume for authentication data
podman volume create notebooklm-chrome-data

# Run the container (stdio mode for local use)
podman run -d \
  --name notebooklm-mcp \
  --restart unless-stopped \
  -e NOTEBOOKLM_HEADLESS=true \
  -e LOG_LEVEL=INFO \
  -v notebooklm-chrome-data:/app/chrome-user-data \
  notebooklm-mcp:latest

# Authenticate with Google
podman exec -it notebooklm-mcp uv run python scripts/setup_auth.py

# View logs
podman logs -f notebooklm-mcp

# Stop and remove
podman stop notebooklm-mcp
podman rm notebooklm-mcp
```

### Testing HTTP Mode Locally

```bash
# Run in HTTP mode for testing
podman run -d \
  --name notebooklm-mcp-http \
  -p 8080:8080 \
  -e MCP_TRANSPORT=streamable-http \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8080 \
  -e NOTEBOOKLM_HEADLESS=true \
  -v notebooklm-chrome-data:/app/chrome-user-data \
  notebooklm-mcp:latest

# Test health endpoint
curl http://localhost:8080/health

# Connect with MCP Inspector
npx @modelcontextprotocol/inspector http://localhost:8080/mcp
```

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

## HTTP Mode for Container Deployments (Experimental)

⚠️ **Note**: HTTP mode is experimental and primarily for local container testing. Multi-user Kubernetes/OpenShift deployments face authentication challenges without an official NotebookLM API.

The MCP server supports HTTP transport for containerized deployments.

### Running in HTTP Mode

```bash
export MCP_TRANSPORT=streamable-http
uv run notebooklm-mcp
```

Server available at: http://localhost:8080/mcp

### Health Check Endpoints

- `GET /health` - Liveness probe
- `GET /readiness` - Readiness probe

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| MCP_TRANSPORT | stdio | "stdio" or "streamable-http" |
| MCP_HOST | 0.0.0.0 | HTTP bind address |
| MCP_PORT | 8080 | HTTP port |

For detailed deployment instructions, see:
- [docs/README_DEPLOYMENT.md](docs/README_DEPLOYMENT.md) - Kubernetes deployment
- [docs/OPENSHIFT_DEPLOYMENT.md](docs/OPENSHIFT_DEPLOYMENT.md) - OpenShift deployment

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

### Common Issues

#### MCP server not showing in Claude Desktop

1. Check Claude Desktop config file location:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Verify JSON syntax is valid (no trailing commas)

3. Check the path in config points to your project directory

4. Restart Claude Desktop completely (quit and reopen)

5. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/mcp*.log`
   - Windows: `%APPDATA%\Claude\logs\mcp*.log`

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

#### Tools not responding in Claude

1. Check if MCP server process is running
2. Try simple tool first: "List my NotebookLM notebooks"
3. Check for errors in Claude Desktop logs
4. Restart the MCP server by restarting Claude Desktop

#### Podman/Container issues

```bash
# Check container logs
podman logs -f notebooklm-mcp

# Exec into container to debug
podman exec -it notebooklm-mcp /bin/bash

# Verify chrome-user-data volume
podman volume inspect notebooklm-chrome-data
```

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
