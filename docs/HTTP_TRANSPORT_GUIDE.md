# HTTP Transport Guide

This guide explains how to run the NotebookLM MCP server in HTTP mode and connect to it from multiple projects.

## Overview

The NotebookLM MCP server supports two transport modes:

1. **Stdio (Default)** - Each project spawns its own server instance
2. **HTTP** - One server instance shared across multiple projects

## When to Use HTTP Transport

Use HTTP transport when:
- ✅ You want to **share one server** across multiple projects
- ✅ You're working on **multiple applications** simultaneously
- ✅ You want to **keep the server running** independently
- ✅ You need **remote access** to the MCP server
- ✅ You want to **reduce resource usage** (one instance vs many)

Use Stdio transport when:
- ✅ You want **automatic server lifecycle** (starts/stops with Claude Code)
- ✅ You're working on **one project** at a time
- ✅ You prefer **simpler configuration** (no server management)

## HTTP Transport Setup

### Step 1: Start the Server

Start the MCP server in HTTP mode (in a dedicated terminal):

```bash
# Navigate to notebooklm-mcp directory
cd /path/to/notebooklm-mcp

# Start server in HTTP mode
MCP_TRANSPORT=streamable-http uv run notebooklm-mcp

# Server will run at: http://localhost:8080/mcp
```

**Server output:**
```
Starting MCP server 'notebooklm' with transport 'streamable-http'
on http://0.0.0.0:8080/mcp
```

**Keep this terminal running** - the server needs to stay active for your projects to use it.

### Step 2: Configure Your Project

In any project directory, create or update `.mcp.json`:

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

### Step 3: Use Claude Code

```bash
# In your project directory
cd /path/to/your-app

# Verify MCP server is connected
claude mcp list

# Start using NotebookLM tools!
```

## Configuration Options

### Custom Port

```bash
# Start on custom port
MCP_TRANSPORT=streamable-http MCP_PORT=9000 uv run notebooklm-mcp
```

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

### Custom Host (Remote Access)

```bash
# Bind to all interfaces (accessible from network)
MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 MCP_PORT=8080 uv run notebooklm-mcp
```

```json
{
  "mcpServers": {
    "notebooklm": {
      "type": "http",
      "url": "http://your-server-ip:8080/mcp"
    }
  }
}
```

### Environment Variables

You can use environment variables in `.mcp.json`:

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

## Running as Background Service

### macOS/Linux - Using screen

```bash
# Start in screen session
screen -dmS notebooklm-mcp bash -c "cd /path/to/notebooklm-mcp && MCP_TRANSPORT=streamable-http uv run notebooklm-mcp"

# Reattach to see logs
screen -r notebooklm-mcp

# Detach: Ctrl+A, then D

# Kill session
screen -X -S notebooklm-mcp quit
```

### macOS/Linux - Using tmux

```bash
# Start in tmux session
tmux new-session -d -s notebooklm-mcp "cd /path/to/notebooklm-mcp && MCP_TRANSPORT=streamable-http uv run notebooklm-mcp"

# Attach to see logs
tmux attach -t notebooklm-mcp

# Detach: Ctrl+B, then D

# Kill session
tmux kill-session -t notebooklm-mcp
```

### macOS - Using launchd (Auto-start on login)

Create `~/Library/LaunchAgents/com.notebooklm.mcp.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.notebooklm.mcp</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/uv</string>
        <string>run</string>
        <string>notebooklm-mcp</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>MCP_TRANSPORT</key>
        <string>streamable-http</string>
        <key>MCP_PORT</key>
        <string>8080</string>
    </dict>
    <key>WorkingDirectory</key>
    <string>/path/to/notebooklm-mcp</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/notebooklm-mcp.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/notebooklm-mcp-error.log</string>
</dict>
</plist>
```

Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.notebooklm.mcp.plist

# Unload
launchctl unload ~/Library/LaunchAgents/com.notebooklm.mcp.plist
```

### Linux - Using systemd

Create `/etc/systemd/user/notebooklm-mcp.service`:

```ini
[Unit]
Description=NotebookLM MCP Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/notebooklm-mcp
Environment="MCP_TRANSPORT=streamable-http"
Environment="MCP_PORT=8080"
ExecStart=/usr/bin/uv run notebooklm-mcp
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

Enable and start:
```bash
systemctl --user enable notebooklm-mcp
systemctl --user start notebooklm-mcp

# Check status
systemctl --user status notebooklm-mcp

# View logs
journalctl --user -u notebooklm-mcp -f
```

## Health Checks

The HTTP server provides health endpoints:

```bash
# Check if server is healthy
curl http://localhost:8080/health

# Response:
# {
#   "status": "healthy",
#   "transport": "streamable-http",
#   "headless": true
# }

# Check readiness
curl http://localhost:8080/readiness
```

## Multiple Project Example

**Terminal 1: Start the server**
```bash
cd ~/notebooklm-mcp
MCP_TRANSPORT=streamable-http uv run notebooklm-mcp
```

**Terminal 2: Project A**
```bash
cd ~/projects/my-app
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "notebooklm": {
      "type": "http",
      "url": "http://localhost:8080/mcp"
    }
  }
}
EOF

# Use Claude Code here
claude
```

**Terminal 3: Project B**
```bash
cd ~/projects/another-app
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "notebooklm": {
      "type": "http",
      "url": "http://localhost:8080/mcp"
    }
  }
}
EOF

# Use Claude Code here too - same server!
claude
```

Both projects now share the same NotebookLM MCP server instance! 🎉

## Comparison: Stdio vs HTTP

| Feature | Stdio (Default) | HTTP |
|---------|----------------|------|
| **Configuration** | Simple - command in .mcp.json | Manual - start server separately |
| **Lifecycle** | Automatic (starts/stops with Claude Code) | Manual (you manage it) |
| **Resource Usage** | One instance per project | One shared instance |
| **Multiple Projects** | Each has own instance | All share one instance |
| **Setup Complexity** | Low | Medium |
| **Remote Access** | Not possible | Possible |
| **Authentication State** | Isolated per project | Shared across projects |

## Troubleshooting

### Server Not Starting

```bash
# Check if port is already in use
lsof -ti:8080

# Kill existing process
lsof -ti:8080 | xargs kill -9

# Try a different port
MCP_TRANSPORT=streamable-http MCP_PORT=9000 uv run notebooklm-mcp
```

### Connection Failed

```bash
# Verify server is running
curl http://localhost:8080/health

# Check firewall (macOS)
sudo pfctl -s all | grep 8080

# Check firewall (Linux)
sudo iptables -L -n | grep 8080
```

### Authentication Issues

The HTTP server shares authentication state. If you get auth errors:

```bash
# Stop the server
# Re-run authentication
cd /path/to/notebooklm-mcp
uv run python scripts/setup_auth.py

# Restart the server
MCP_TRANSPORT=streamable-http uv run notebooklm-mcp
```

## Security Considerations

When running in HTTP mode:

⚠️ **Local Network Access**
- By default, binds to `0.0.0.0` (all interfaces)
- Anyone on your network can access the server
- Use `MCP_HOST=127.0.0.1` to restrict to localhost only

⚠️ **No Built-in Authentication**
- The HTTP endpoint has no authentication
- Don't expose to untrusted networks
- Use SSH tunneling for remote access if needed

⚠️ **Shared Authentication State**
- All projects share the same Google account session
- Browser cookies are shared across all connections

## Best Practices

1. **Use Stdio for Single Projects** - Simpler and automatic
2. **Use HTTP for Multi-Project Work** - More efficient
3. **Run as Service for Daily Use** - Set up systemd/launchd
4. **Monitor with Health Checks** - Verify server is running
5. **Secure Remote Access** - Use SSH tunnels, not direct exposure

## Related Documentation

- [Claude Code Setup](CLAUDE_CODE_SETUP.md) - Quick start with stdio
- [README.md](../README.md) - Main documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide
