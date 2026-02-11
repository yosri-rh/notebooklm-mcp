#!/usr/bin/env python3
"""Extract notebooks using JavaScript evaluation."""
import asyncio
import json
from src.notebooklm_mcp.browser import NotebookLMBrowser


async def extract_with_javascript():
    """Extract notebook data using JavaScript."""
    print("=" * 60)
    print("Extracting notebooks using JavaScript")
    print("=" * 60)

    async with NotebookLMBrowser(headless=False) as browser:
        # Navigate to NotebookLM home
        print("\n[1/2] Navigating to NotebookLM...")
        await browser.goto("https://notebooklm.google.com")
        await browser.page.wait_for_timeout(5000)

        # Use JavaScript to extract notebook data
        print("\n[2/2] Extracting data with JavaScript...")

        # Extract data from table rows
        notebooks_data = await browser.page.evaluate('''() => {
            const rows = document.querySelectorAll('tr[mat-row]');
            const notebooks = [];

            rows.forEach((row, index) => {
                try {
                    // Get title
                    const titleEl = row.querySelector('.project-table-title');
                    const title = titleEl ? titleEl.innerText.trim() : '';

                    // Get sources count
                    const sourcesEl = row.querySelector('.sources-column');
                    const sources = sourcesEl ? sourcesEl.innerText.trim() : '';

                    // Get created date
                    const createdEl = row.querySelector('.created-time-column');
                    const created = createdEl ? createdEl.innerText.trim() : '';

                    // Get role
                    const roleEl = row.querySelector('.role-column');
                    const role = roleEl ? roleEl.innerText.trim() : '';

                    // Try to find notebook ID in various ways
                    // 1. Check if row has onclick handler or data attributes
                    const rowAttrs = {};
                    for (let attr of row.attributes) {
                        rowAttrs[attr.name] = attr.value;
                    }

                    // 2. Check Angular component data (if accessible)
                    let notebookId = null;
                    if (row.__ngContext__) {
                        // Try to extract from Angular context
                        const context = row.__ngContext__;
                        if (Array.isArray(context)) {
                            // Look through context for project/notebook data
                            context.forEach(item => {
                                if (item && typeof item === 'object') {
                                    if (item.id || item.projectId || item.notebookId) {
                                        notebookId = item.id || item.projectId || item.notebookId;
                                    }
                                }
                            });
                        }
                    }

                    notebooks.push({
                        index: index + 1,
                        title: title,
                        sources: sources,
                        created: created,
                        role: role,
                        notebookId: notebookId,
                        rowAttrs: rowAttrs
                    });
                } catch (e) {
                    console.error('Error processing row:', e);
                }
            });

            return notebooks;
        }''')

        print(f"\nExtracted {len(notebooks_data)} notebooks:\n")
        print(json.dumps(notebooks_data, indent=2))

        # Now try clicking each row in a better way
        print("\n" + "=" * 60)
        print("Attempting to click rows to get URLs...")
        print("=" * 60)

        final_notebooks = []

        rows = await browser.page.query_selector_all('tr[mat-row]')
        for i, row in enumerate(rows):
            try:
                # Get fresh page reference
                await browser.page.goto("https://notebooklm.google.com")
                await browser.page.wait_for_timeout(3000)

                # Get all rows again
                rows_fresh = await browser.page.query_selector_all('tr[mat-row]')
                if i >= len(rows_fresh):
                    continue

                row_fresh = rows_fresh[i]

                print(f"\nNotebook {i+1}/{len(rows)}:")

                # Try clicking the title specifically
                title_cell = await row_fresh.query_selector('td.title-column')
                if title_cell:
                    print("  Clicking title cell...")

                    # Get current URL before click
                    url_before = browser.page.url

                    # Click and wait for navigation
                    await title_cell.click()
                    await browser.page.wait_for_timeout(3000)

                    # Get new URL
                    url_after = browser.page.url

                    if url_after != url_before and "/notebook/" in url_after:
                        notebook_id = url_after.split("/notebook/")[-1].split("?")[0].split("#")[0]

                        final_notebooks.append({
                            "id": notebook_id,
                            "title": notebooks_data[i]['title'],
                            "url": url_after,
                            "sources": notebooks_data[i]['sources'],
                            "created": notebooks_data[i]['created'],
                            "role": notebooks_data[i]['role']
                        })

                        print(f"  ✓ ID: {notebook_id}")
                        print(f"  ✓ URL: {url_after}")
                    else:
                        print(f"  ✗ No navigation (URL stayed: {url_after})")

            except Exception as e:
                print(f"  ✗ Error: {e}")

        print("\n" + "=" * 60)
        print(f"FINAL RESULTS: {len(final_notebooks)} notebooks")
        print("=" * 60)
        print(json.dumps(final_notebooks, indent=2))

        print("\n" + "=" * 60)
        print("Browser will stay open for 10 seconds")
        print("=" * 60)
        await browser.page.wait_for_timeout(10000)

        return final_notebooks


if __name__ == "__main__":
    try:
        asyncio.run(extract_with_javascript())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
