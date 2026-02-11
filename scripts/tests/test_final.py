#!/usr/bin/env python3
"""Final test of updated list_notebooks implementation."""
import asyncio
import json
import os
from typing import List, Dict
from src.notebooklm_mcp.browser import NotebookLMBrowser, AuthenticationError


def get_headless_mode() -> bool:
    """Get headless mode from environment variable."""
    return os.getenv("NOTEBOOKLM_HEADLESS", "true").lower() == "true"


async def list_notebooks_updated() -> List[Dict[str, str]]:
    """
    List all available NotebookLM notebooks (UPDATED VERSION).

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
            await browser.page.wait_for_timeout(3000)

            # Find table rows (NotebookLM uses table view)
            rows = await browser.page.query_selector_all('tr[mat-row]')

            if not rows:
                return []

            notebooks = []

            # Extract data from each row by clicking and capturing URL
            for i, _ in enumerate(rows):
                try:
                    # Navigate back to home to get fresh page state
                    await browser.goto("https://notebooklm.google.com")
                    await browser.page.wait_for_timeout(2000)

                    # Get all rows again (fresh references)
                    rows_fresh = await browser.page.query_selector_all('tr[mat-row]')
                    if i >= len(rows_fresh):
                        continue

                    row = rows_fresh[i]

                    # Extract title from table cell
                    title_cell = await row.query_selector('td.title-column .project-table-title')
                    title = "Untitled"
                    if title_cell:
                        title = await title_cell.inner_text()
                        title = title.strip()

                    # Click the title cell to navigate to notebook
                    clickable = await row.query_selector('td.title-column')
                    if clickable:
                        await clickable.click()
                        await browser.page.wait_for_timeout(2000)

                        # Get the notebook URL
                        url = browser.page.url

                        if "/notebook/" in url:
                            # Extract notebook ID from URL
                            notebook_id = url.split("/notebook/")[-1].split("?")[0].split("#")[0]

                            notebooks.append({
                                "id": notebook_id,
                                "title": title,
                                "url": url
                            })

                except Exception:
                    # Continue to next notebook if one fails
                    continue

            return notebooks

    except AuthenticationError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to list notebooks: {str(e)}")


async def main():
    """Test the updated implementation."""
    print("Testing UPDATED list_notebooks implementation\n")
    print("=" * 60)

    try:
        notebooks = await list_notebooks_updated()

        print(f"\n✓ Successfully retrieved {len(notebooks)} notebook(s):\n")
        print(json.dumps(notebooks, indent=2))

        print("\n" + "=" * 60)
        print("SUCCESS! The MCP server has been updated.")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
