#!/usr/bin/env python3
"""Test the running MCP server by making a direct function call."""
import asyncio
import sys
import os

# Set environment variable
os.environ['NOTEBOOKLM_HEADLESS'] = 'true'

async def test_server():
    """Test by calling the function directly."""
    print("=" * 70)
    print("Testing Running MCP Server Functions")
    print("=" * 70)
    print()
    
    try:
        # Import the server module
        from src.notebooklm_mcp.server import list_notebooks
        
        print("Calling list_notebooks()...")
        notebooks = await list_notebooks()
        
        print(f"✅ Successfully retrieved {len(notebooks)} notebook(s)")
        print()
        
        for i, nb in enumerate(notebooks, 1):
            print(f"{i}. {nb.get('title', 'Untitled')}")
            print(f"   ID: {nb.get('id', 'N/A')}")
            print(f"   URL: {nb.get('url', 'N/A')}")
            print()
        
        print("=" * 70)
        print("✅ MCP Server Functions: WORKING")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_server())
    sys.exit(0 if result else 1)
