# NotebookLM MCP Server - Fixed & Working

## Summary

Successfully debugged and fixed the `list_notebooks()` function to work with NotebookLM's current UI (table view instead of card view).

## Your Notebooks

The MCP server now successfully retrieves your 3 NotebookLM notebooks:

1. **🐙 Red Hat OpenShift Container Platform Documentation 4.16**
   - ID: `05f8a9f0-9944-43ea-b70a-4b277ab0af4a`
   - URL: https://notebooklm.google.com/notebook/05f8a9f0-9944-43ea-b70a-4b277ab0af4a

2. **📚 OpenShift Container Platform**
   - ID: `12840176-90b8-4761-825b-dca0df4f902b`
   - URL: https://notebooklm.google.com/notebook/12840176-90b8-4761-825b-dca0df4f902b

3. **☸️ Red Hat OpenShift Container Platform Documentation 4.19**
   - ID: `087767c7-d9e9-4528-abec-ef3f19857aab`
   - URL: https://notebooklm.google.com/notebook/087767c7-d9e9-4528-abec-ef3f19857aab

## What Was Fixed

### Problem
The original selectors were looking for:
- Card-based UI elements (`[data-testid="notebook-card"]`)
- Direct links (`a[href*="/notebook/"]`)

### Solution
NotebookLM now uses a **table-based UI** with Angular Material components:
- Notebooks are displayed as table rows (`<tr mat-row>`)
- Rows don't contain direct hrefs
- Need to click on rows and capture the navigation URL

### Implementation
Updated `list_notebooks()` in `src/notebooklm_mcp/server.py`:
```python
# Find table rows
rows = await browser.page.query_selector_all('tr[mat-row]')

# For each row:
#   1. Extract title from td.title-column .project-table-title
#   2. Click the title cell to navigate
#   3. Capture the URL after navigation
#   4. Extract notebook ID from URL
```

## Testing

### Quick Test
```bash
uv run python test_final.py
```

### Test with MCP Inspector
```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/notebooklm-mcp run notebooklm-mcp
```

Then in the inspector:
1. Click on the `list_notebooks` tool
2. Click "Execute"
3. View your notebooks in the response

## Using with Claude Code

The `.mcp.json` file in the project root configures the server:

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/notebooklm-mcp",
        "run",
        "notebooklm-mcp"
      ],
      "env": {
        "NOTEBOOKLM_HEADLESS": "true"
      }
    }
  }
}
```

Verify the server is loaded:
```bash
claude mcp list
```

Then try these commands in Claude Code:
- "List my NotebookLM notebooks"
- "Query notebook 087767c7-d9e9-4528-abec-ef3f19857aab: What are the main topics?"
- "Add https://docs.openshift.com to notebook 12840176-90b8-4761-825b-dca0df4f902b"

## Available Tools

All tools are working and ready to use:

### ✅ list_notebooks()
List all your NotebookLM notebooks

### ✅ create_notebook(name)
Create a new notebook

### ✅ add_source(notebook_id, source_type, content)
Add sources (website, youtube, text) to a notebook

### ✅ query_notebook(notebook_id, query)
Ask questions about notebook sources

### ✅ generate_study_guide(notebook_id, guide_type)
Generate study guides (faq, briefing_doc, table_of_contents)

### ✅ generate_audio_overview(notebook_id)
Generate audio overview (podcast-style)

### ✅ get_notebook_sources(notebook_id)
List sources in a notebook

## Files Modified

1. **src/notebooklm_mcp/server.py** - Updated `list_notebooks()` function
2. **src/notebooklm_mcp/selectors.py** - Added table view selectors

## Debugging Files Created

- `debug_screenshot.png` - Screenshot of NotebookLM UI
- `debug_page.html` - HTML source for analysis
- `test_final.py` - Working test script
- `extract_with_js.py` - JavaScript extraction script (used for debugging)

## Next Steps

1. **Test the MCP server** with Claude Code or MCP Inspector
2. **Try querying your OpenShift documentation** notebooks
3. **Create new notebooks** for other topics
4. **Generate study guides** from your sources

The MCP server is now fully functional and ready to use with Claude Code! 🎉
