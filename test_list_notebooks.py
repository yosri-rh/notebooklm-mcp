#!/usr/bin/env python3
"""Test script to list NotebookLM notebooks."""
import asyncio
import sys
import json
import os
from src.notebooklm_mcp.browser import NotebookLMBrowser, AuthenticationError
from src.notebooklm_mcp.selectors import Selectors, find_element, find_all_elements


def get_headless_mode() -> bool:
    """Get headless mode from environment variable."""
    return os.getenv("NOTEBOOKLM_HEADLESS", "true").lower() == "true"


async def list_notebooks_test():
    """
    List all available NotebookLM notebooks.

    Returns:
        List of notebooks with id, title, and url
    """
    try:
        async with NotebookLMBrowser(headless=get_headless_mode()) as browser:
            # Check authentication
            is_authenticated = await browser.check_authentication()
            if not is_authenticated:
                raise AuthenticationError(
                    "Not authenticated. Run: python scripts/setup_auth.py"
                )

            # Navigate to NotebookLM home (shows all notebooks)
            await browser.goto("https://notebooklm.google.com")

            # Wait for notebooks to load
            await browser.page.wait_for_timeout(3000)

            # Find all notebook cards
            notebook_elements = await find_all_elements(
                browser.page,
                Selectors.NOTEBOOK_LIST,
                timeout=10000
            )

            if not notebook_elements:
                return []

            notebooks = []
            for element in notebook_elements:
                try:
                    # Extract notebook URL
                    url = await element.get_attribute("href")
                    if not url:
                        # Try finding link within element
                        link = await element.query_selector("a[href*='/notebook/']")
                        if link:
                            url = await link.get_attribute("href")

                    if url and "/notebook/" in url:
                        # Extract notebook ID from URL
                        notebook_id = url.split("/notebook/")[-1].split("?")[0]

                        # Extract title
                        title_element = await element.query_selector("h2, h3, [role='heading']")
                        title = "Untitled"
                        if title_element:
                            title = await title_element.inner_text()

                        notebooks.append({
                            "id": notebook_id,
                            "title": title.strip(),
                            "url": f"https://notebooklm.google.com/notebook/{notebook_id}"
                        })
                except Exception:
                    continue

            return notebooks

    except AuthenticationError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to list notebooks: {str(e)}")


async def main():
    """Test the list_notebooks tool."""
    print("Testing NotebookLM MCP server - list_notebooks()\n")
    print("=" * 60)

    try:
        notebooks = await list_notebooks_test()

        print(f"\n✓ Successfully retrieved {len(notebooks)} notebook(s):\n")
        print(json.dumps(notebooks, indent=2))

    except AuthenticationError as e:
        print(f"\n✗ Authentication Error: {str(e)}")
        print("\n" + "=" * 60)
        print("AUTHENTICATION REQUIRED")
        print("=" * 60)
        print("\nPlease run this command in your terminal:")
        print("  uv run python scripts/setup_auth.py")
        print("\nThen follow the browser prompts to sign in to Google.")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print(f"\nError type: {type(e).__name__}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
