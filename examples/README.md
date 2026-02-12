# Example MCP Configurations

This directory contains example `.mcp.json` configuration files for different use cases.

## Available Examples

### `mcp-stdio.json` - Default (Recommended)

Uses stdio transport where Claude Code automatically manages the server lifecycle.

**When to use:**
- ✅ Working on one project at a time
- ✅ You want automatic server management
- ✅ Simplest setup

**Setup:**
1. Copy to your project root as `.mcp.json`
2. Update the path to point to your notebooklm-mcp installation
3. Start using Claude Code!

```bash
cp examples/mcp-stdio.json /path/to/your-project/.mcp.json

# Edit the file to update the path:
# Change: "/absolute/path/to/notebooklm-mcp"
# To: "/Users/yourname/notebooklm-mcp"
```

### `mcp-http.json` - Advanced Multi-Project

Uses HTTP transport to connect to a running server instance.

**When to use:**
- ✅ Working on multiple projects simultaneously
- ✅ Want to share one server across projects
- ✅ Need to reduce resource usage

**Setup:**
1. Start the HTTP server once:
   ```bash
   cd /path/to/notebooklm-mcp
   MCP_TRANSPORT=streamable-http uv run notebooklm-mcp
   ```

2. Copy this config to any project:
   ```bash
   cp examples/mcp-http.json /path/to/your-project/.mcp.json
   ```

3. Use Claude Code in that project!

📖 **Full guide:** See [HTTP Transport Guide](../docs/HTTP_TRANSPORT_GUIDE.md)

## Quick Comparison

| Feature | stdio (mcp-stdio.json) | HTTP (mcp-http.json) |
|---------|------------------------|----------------------|
| **Setup** | Copy once per project | Start server + copy config |
| **Server** | Auto-managed | You manage it |
| **Projects** | One instance per project | Shared instance |
| **Resources** | Multiple instances | Single instance |
| **Best for** | Single project work | Multi-project work |

## Creating Your Own

You can customize these examples:

### Custom Environment Variables (stdio)

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "uv",
      "args": ["--directory", "/path/to/notebooklm-mcp", "run", "notebooklm-mcp"],
      "env": {
        "NOTEBOOKLM_HEADLESS": "false",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Custom Port (HTTP)

```json
{
  "mcpServers": {
    "notebooklm": {
      "type": "http",
      "url": "http://localhost:9000/mcp"
    }
  }
}
```

Then start server on that port:
```bash
MCP_TRANSPORT=streamable-http MCP_PORT=9000 uv run notebooklm-mcp
```

### Using Environment Variables

```json
{
  "mcpServers": {
    "notebooklm": {
      "type": "http",
      "url": "${NOTEBOOKLM_URL:-http://localhost:8080}/mcp"
    }
  }
}
```

Set the variable:
```bash
export NOTEBOOKLM_URL=http://localhost:8080
```

## Related Documentation

- [Claude Code Setup](../docs/CLAUDE_CODE_SETUP.md) - Quick start guide
- [HTTP Transport Guide](../docs/HTTP_TRANSPORT_GUIDE.md) - Detailed HTTP setup
- [Main README](../README.md) - Full documentation
