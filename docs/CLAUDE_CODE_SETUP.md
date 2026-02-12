# NotebookLM MCP Integration with Claude Code

Simple guide for using NotebookLM with Claude Code CLI.

## What This Does

This MCP server allows you to interact with Google NotebookLM directly from Claude Code. You can:
- Create and list notebooks
- Add sources (websites, YouTube videos, text)
- Query notebooks with AI
- Generate study guides and audio overviews

## Quick Setup

### 1. Install Dependencies

```bash
# From the project directory
uv sync
uv run playwright install chromium
```

### 2. Authenticate with Google

Run this once to log into your Google account:

```bash
uv run python scripts/setup_auth.py
```

This will:
- Open a browser window
- Ask you to sign in to Google
- Navigate to https://notebooklm.google.com
- Save your session for future use

### 3. Enable the MCP Server

The `.mcp.json` file is already configured. Just restart Claude Code or run:

```bash
# Check available MCP servers
claude mcp list
```

You should see `notebooklm` in the list.

### 4. Test It

In Claude Code, try:

```
List my NotebookLM notebooks
```

or

```
Create a new NotebookLM notebook called "Test Notebook"
```

## Available Tools

Once enabled, you can use these commands naturally in conversation:

### List Notebooks
```
Show me all my NotebookLM notebooks
```

### Create Notebook
```
Create a new notebook called "AI Research"
```

### Add Sources
```
Add https://example.com to notebook [id]
```

```
Add YouTube video https://youtube.com/watch?v=... to notebook [id]
```

```
Add this text to notebook [id]: "Your custom text content here"
```

### Query Notebook
```
Ask notebook [id]: What are the main topics discussed?
```

### Generate Study Materials
```
Generate a FAQ study guide for notebook [id]
```

```
Generate an audio overview for notebook [id]
```

### Get Sources
```
Show me all sources in notebook [id]
```

## Troubleshooting

### Authentication Issues

If you get authentication errors:

```bash
# Re-run the authentication setup
uv run python scripts/setup_auth.py
```

### MCP Server Not Found

Check that `.mcp.json` exists in the project root:

```bash
cat .mcp.json
```

It should look like:

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/ybenmahf/Documents/mcp-learning/notebooklm-mcp",
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

### See Browser Actions (Debug Mode)

To watch what the browser automation is doing:

```bash
# Run in non-headless mode
NOTEBOOKLM_HEADLESS=false uv run notebooklm-mcp
```

### Playwright Issues

```bash
# Reinstall Chromium
uv run playwright install chromium --force
```

## Advanced: HTTP Transport (Multi-Project)

The default setup uses **stdio transport** where Claude Code automatically manages the server.

For **advanced users** working on multiple projects simultaneously, you can run one shared HTTP server:

```bash
# Start server once (keep running)
cd /path/to/notebooklm-mcp
MCP_TRANSPORT=streamable-http uv run notebooklm-mcp
```

Then in any project, use this `.mcp.json`:
```json
{
  "mcpServers": {
    "notebooklm": {
      "type": "http",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

📖 **See full guide:** [HTTP Transport Guide](HTTP_TRANSPORT_GUIDE.md)

## Configuration

### Environment Variables (Optional)

You can customize behavior with environment variables:

- `NOTEBOOKLM_HEADLESS=true|false` - Show/hide browser (default: true)
- `LOG_LEVEL=DEBUG|INFO|WARNING|ERROR` - Logging verbosity (default: INFO)

Example:

```bash
# Run with visible browser and debug logging
NOTEBOOKLM_HEADLESS=false LOG_LEVEL=DEBUG uv run notebooklm-mcp
```

## Important Notes

- **Browser Automation**: This uses Playwright to automate Chrome/Chromium since NotebookLM has no official API
- **Google Account Required**: You must have a Google account with access to NotebookLM
- **Session Persistence**: Your Google session is saved in `chrome-user-data/` (gitignored)
- **Personal Use**: This is for personal/educational use only

## How It Works

```
Claude Code (you)
    ↓
MCP Server (notebooklm-mcp)
    ↓
Playwright + Chromium (browser automation)
    ↓
NotebookLM Web UI (https://notebooklm.google.com)
```

The MCP server uses browser automation to interact with NotebookLM's web interface since there's no official API available for the free version.
