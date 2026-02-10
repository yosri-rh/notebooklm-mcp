#!/usr/bin/env python3
"""
Interactive authentication setup for NotebookLM.
Run this script once to sign in to your Google account.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def setup_authentication():
    """Open browser for Google sign-in and save persistent session."""
    user_data_dir = Path(__file__).parent.parent / "chrome-user-data"
    user_data_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("NotebookLM Authentication Setup")
    print("=" * 60)
    print(f"\nBrowser profile will be saved to: {user_data_dir}")
    print("\nOpening browser for Google sign-in...")
    print("Please complete the following steps:")
    print("  1. Sign in to your Google account")
    print("  2. Navigate to https://notebooklm.google.com")
    print("  3. Verify you can access NotebookLM")
    print("  4. Press Enter in this terminal when done")
    print("=" * 60)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
            ]
        )
        page = await context.new_page()
        await page.goto("https://notebooklm.google.com")

        print("\n✓ Browser opened. Complete sign-in and press Enter...")
        input()

        print("\n✓ Authentication saved!")
        print(f"✓ Session stored in: {user_data_dir}")
        print("\nYou can now run the MCP server:")
        print("  uv run notebooklm-mcp")

        await context.close()


if __name__ == "__main__":
    asyncio.run(setup_authentication())
