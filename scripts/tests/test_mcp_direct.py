#!/usr/bin/env python3
"""Direct test of NotebookLM functions."""
import asyncio
import sys
import os

# Set headless mode
os.environ['NOTEBOOKLM_HEADLESS'] = 'true'

async def test_list_notebooks():
    """Test listing notebooks directly."""
    from src.notebooklm_mcp.browser import NotebookLMBrowser
    
    print("=" * 70)
    print("Testing NotebookLM MCP Server - Direct Function Test")
    print("=" * 70)
    print()
    
    print("📋 Test: List Notebooks")
    print("-" * 70)
    
    try:
        async with NotebookLMBrowser(headless=True) as browser:
            # Check authentication
            print("Checking authentication...")
            is_auth = await browser.check_authentication()
            
            if not is_auth:
                print("❌ FAILED: Not authenticated")
                print("   Run: uv run python scripts/setup_auth.py")
                return False
            
            print("✅ Authentication: OK")
            
            # Navigate to NotebookLM
            print("Navigating to NotebookLM...")
            await browser.goto("https://notebooklm.google.com")
            await browser.page.wait_for_timeout(3000)
            
            # Find notebooks
            print("Searching for notebooks...")
            rows = await browser.page.query_selector_all('tr[mat-row]')
            
            print(f"✅ Found {len(rows)} notebook(s)")
            print()
            
            if len(rows) > 0:
                print("Sample notebooks:")
                for i, _ in enumerate(rows[:3]):  # Show first 3
                    await browser.goto("https://notebooklm.google.com")
                    await browser.page.wait_for_timeout(2000)
                    
                    rows_fresh = await browser.page.query_selector_all('tr[mat-row]')
                    if i < len(rows_fresh):
                        row = rows_fresh[i]
                        title_cell = await row.query_selector('td.title-column .project-table-title')
                        
                        if title_cell:
                            title = await title_cell.inner_text()
                            print(f"  {i+1}. {title.strip()}")
            
            print()
            print("=" * 70)
            print("✅ MCP Server Test: PASSED")
            print("=" * 70)
            print()
            print("Server is ready to use with:")
            print("  - Claude Desktop integration")
            print("  - MCP Inspector")
            print("  - Direct API calls")
            print()
            
            return True
            
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_list_notebooks())
    sys.exit(0 if result else 1)
