#!/usr/bin/env python3
"""Test MCP server tools using uv environment."""
import asyncio
import sys

async def main():
    print("=" * 70)
    print("Testing MCP Server - Tool Execution")
    print("=" * 70)
    print()
    
    # Import and test list_notebooks
    from src.notebooklm_mcp.server import list_notebooks
    
    print("📋 Executing: list_notebooks()")
    print("-" * 70)
    
    try:
        notebooks = await list_notebooks()
        
        print(f"✅ Success! Found {len(notebooks)} notebook(s)")
        print()
        
        if notebooks:
            for i, nb in enumerate(notebooks, 1):
                print(f"{i}. {nb.get('title', 'Untitled')}")
                print(f"   ID: {nb.get('id', 'N/A')[:20]}...")
        else:
            print("   No notebooks found")
        
        print()
        print("=" * 70)
        print("✅ MCP Server Test: PASSED")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
