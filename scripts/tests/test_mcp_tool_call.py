#!/usr/bin/env python3
"""Test MCP server tool call."""
import asyncio
import json
import sys

async def test_tool_call():
    """Test calling list_notebooks tool."""
    print("=" * 70)
    print("Testing MCP Tool Call: list_notebooks")
    print("=" * 70)
    print()
    
    # Start MCP server
    print("Starting MCP server...")
    proc = await asyncio.create_subprocess_exec(
        "uv", "run", "notebooklm-mcp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Initialize
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        proc.stdin.write((json.dumps(initialize_request) + "\n").encode())
        await proc.stdin.drain()
        await proc.stdout.readline()  # Read initialize response
        
        # Call list_notebooks tool
        print("Calling list_notebooks tool...")
        tool_call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "list_notebooks",
                "arguments": {}
            }
        }
        
        proc.stdin.write((json.dumps(tool_call_request) + "\n").encode())
        await proc.stdin.drain()
        
        # Read response
        response_line = await asyncio.wait_for(proc.stdout.readline(), timeout=30.0)
        response = json.loads(response_line.decode())
        
        if 'result' in response:
            content = response['result'].get('content', [])
            if content:
                text = content[0].get('text', '')
                notebooks = json.loads(text) if text else []
                
                print(f"✅ Tool call successful!")
                print(f"   Found {len(notebooks)} notebook(s)")
                for nb in notebooks[:3]:
                    print(f"   - {nb.get('title', 'Untitled')}")
                print()
                
                print("=" * 70)
                print("✅ MCP Tool Call: SUCCESSFUL")
                print("=" * 70)
                return True
        else:
            print(f"❌ Error: {response.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=2.0)
        except:
            proc.kill()

if __name__ == "__main__":
    result = asyncio.run(test_tool_call())
    sys.exit(0 if result else 1)
