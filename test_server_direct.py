#!/usr/bin/env python3
"""Test the actual MCP server list_notebooks function."""
import asyncio
import json
import sys


async def main():
    """Test the list_notebooks function from the server."""
    print("Testing updated MCP server - list_notebooks()\n")
    print("=" * 60)

    try:
        # Import the actual server module
        from src.notebooklm_mcp import server

        # Get the actual tool implementation
        # The @mcp.tool() decorator wraps the function, so we need to call it directly
        from src.notebooklm_mcp.server import list_notebooks

        # Call the actual async function
        notebooks = await list_notebooks()

        print(f"\n✓ Successfully retrieved {len(notebooks)} notebook(s):\n")
        print(json.dumps(notebooks, indent=2))

        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print(f"\nError type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
