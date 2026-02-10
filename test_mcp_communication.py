#!/usr/bin/env python3
"""Test MCP server communication."""
import asyncio
import json
import sys
import subprocess

async def test_mcp_server():
    """Test MCP server initialization and tool listing."""
    print("=" * 70)
    print("Testing MCP Server Communication")
    print("=" * 70)
    print()
    
    # Start MCP server process
    print("Starting MCP server...")
    proc = await asyncio.create_subprocess_exec(
        "uv", "run", "notebooklm-mcp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Send initialize request
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("Sending initialize request...")
        request_json = json.dumps(initialize_request) + "\n"
        proc.stdin.write(request_json.encode())
        await proc.stdin.drain()
        
        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)
            response = json.loads(response_line.decode())
            
            print("✅ Server responded to initialize")
            print(f"   Protocol Version: {response.get('result', {}).get('protocolVersion', 'N/A')}")
            print(f"   Server Name: {response.get('result', {}).get('serverInfo', {}).get('name', 'N/A')}")
            print()
            
            # Send list tools request
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            print("Requesting tools list...")
            request_json = json.dumps(list_tools_request) + "\n"
            proc.stdin.write(request_json.encode())
            await proc.stdin.drain()
            
            # Read tools response
            response_line = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)
            response = json.loads(response_line.decode())
            
            tools = response.get('result', {}).get('tools', [])
            print(f"✅ Server provided {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool.get('name', 'unknown')}")
            print()
            
            print("=" * 70)
            print("✅ MCP Server Communication: SUCCESSFUL")
            print("=" * 70)
            
            return True
            
        except asyncio.TimeoutError:
            print("❌ Server did not respond within timeout")
            stderr = await proc.stderr.read()
            if stderr:
                print(f"Server stderr: {stderr.decode()}")
            return False
            
    finally:
        # Cleanup
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()

if __name__ == "__main__":
    result = asyncio.run(test_mcp_server())
    sys.exit(0 if result else 1)
