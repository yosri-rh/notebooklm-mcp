"""NotebookLM MCP Server - Connects Claude to Google NotebookLM."""
import os
from typing import List, Dict, Literal
from fastmcp import FastMCP
from pydantic import Field
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .browser import NotebookLMBrowser, AuthenticationError
from .selectors import Selectors, find_element, find_all_elements


# Initialize FastMCP server
mcp = FastMCP("notebooklm")


def get_headless_mode() -> bool:
    """Get headless mode from environment variable."""
    return os.getenv("NOTEBOOKLM_HEADLESS", "true").lower() == "true"


# ============================================================================
# PHASE 1 TOOLS - Essential Operations
# ============================================================================

@mcp.tool()
async def list_notebooks() -> List[Dict[str, str]]:
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
    except PlaywrightTimeoutError as e:
        raise RuntimeError(f"NotebookLM UI timed out: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to list notebooks: {str(e)}")


@mcp.tool()
async def create_notebook(
    name: str = Field(description="Name for the new notebook")
) -> Dict[str, str]:
    """
    Create a new NotebookLM notebook.

    Args:
        name: Name for the notebook

    Returns:
        Created notebook details (id, title, url)
    """
    try:
        async with NotebookLMBrowser(headless=get_headless_mode()) as browser:
            # Check authentication
            is_authenticated = await browser.check_authentication()
            if not is_authenticated:
                raise AuthenticationError(
                    "Not authenticated. Run: python scripts/setup_auth.py"
                )

            # Navigate to NotebookLM home
            await browser.goto("https://notebooklm.google.com")
            await browser.page.wait_for_timeout(2000)

            # Click create notebook button
            create_button = await find_element(
                browser.page,
                Selectors.CREATE_NOTEBOOK_BUTTON,
                timeout=10000
            )
            await create_button.click()

            # Wait for notebook to be created and page to load
            await browser.page.wait_for_timeout(3000)

            # Try to set notebook name if input is available
            try:
                name_input = await find_element(
                    browser.page,
                    Selectors.NOTEBOOK_NAME_INPUT,
                    timeout=5000
                )
                await name_input.fill(name)
                await name_input.press("Enter")
            except PlaywrightTimeoutError:
                # Some UIs may not have editable name on creation
                # The notebook is still created with default name
                pass

            # Wait for URL to update with notebook ID
            await browser.page.wait_for_timeout(2000)
            current_url = browser.page.url

            if "/notebook/" in current_url:
                notebook_id = current_url.split("/notebook/")[-1].split("?")[0]
                return {
                    "id": notebook_id,
                    "title": name,
                    "url": current_url
                }
            else:
                raise RuntimeError("Failed to create notebook - URL didn't update")

    except AuthenticationError:
        raise
    except PlaywrightTimeoutError as e:
        raise RuntimeError(f"NotebookLM UI timed out: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to create notebook: {str(e)}")


@mcp.tool()
async def add_source(
    notebook_id: str = Field(description="Notebook ID to add source to"),
    source_type: Literal["website", "youtube", "text"] = Field(
        description="Type of source to add"
    ),
    content: str = Field(
        description="Source content (URL for website/youtube, text for text)"
    )
) -> Dict[str, str]:
    """
    Add a source to a NotebookLM notebook.

    Args:
        notebook_id: ID of the notebook
        source_type: Type of source (website, youtube, or text)
        content: URL for website/youtube, or raw text for text source

    Returns:
        Status message
    """
    try:
        async with NotebookLMBrowser(headless=get_headless_mode()) as browser:
            # Check authentication
            is_authenticated = await browser.check_authentication()
            if not is_authenticated:
                raise AuthenticationError(
                    "Not authenticated. Run: python scripts/setup_auth.py"
                )

            # Navigate to notebook
            notebook_url = f"https://notebooklm.google.com/notebook/{notebook_id}"
            await browser.goto(notebook_url)
            await browser.page.wait_for_timeout(2000)

            # Click add source button
            add_button = await find_element(
                browser.page,
                Selectors.ADD_SOURCE_BUTTON,
                timeout=10000
            )
            await add_button.click()
            await browser.page.wait_for_timeout(1000)

            # Select source type
            if source_type == "website":
                type_button = await find_element(
                    browser.page,
                    Selectors.SOURCE_TYPE_URL
                )
                await type_button.click()
                await browser.page.wait_for_timeout(500)

                url_input = await find_element(
                    browser.page,
                    Selectors.SOURCE_URL_INPUT
                )
                await url_input.fill(content)

            elif source_type == "youtube":
                type_button = await find_element(
                    browser.page,
                    Selectors.SOURCE_TYPE_YOUTUBE
                )
                await type_button.click()
                await browser.page.wait_for_timeout(500)

                url_input = await find_element(
                    browser.page,
                    Selectors.SOURCE_URL_INPUT
                )
                await url_input.fill(content)

            elif source_type == "text":
                type_button = await find_element(
                    browser.page,
                    Selectors.SOURCE_TYPE_TEXT
                )
                await type_button.click()
                await browser.page.wait_for_timeout(500)

                text_input = await find_element(
                    browser.page,
                    Selectors.SOURCE_TEXT_INPUT
                )
                await text_input.fill(content)

            # Submit
            submit_button = await find_element(
                browser.page,
                Selectors.SUBMIT_BUTTON
            )
            await submit_button.click()

            # Wait for source to be processed
            await browser.page.wait_for_timeout(3000)

            return {
                "status": "success",
                "message": f"Added {source_type} source to notebook",
                "notebook_id": notebook_id
            }

    except AuthenticationError:
        raise
    except PlaywrightTimeoutError as e:
        raise RuntimeError(f"NotebookLM UI timed out: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to add source: {str(e)}")


@mcp.tool()
async def query_notebook(
    notebook_id: str = Field(description="Notebook ID to query"),
    query: str = Field(description="Question to ask about the notebook sources")
) -> str:
    """
    Ask NotebookLM's AI a question about notebook sources.

    Args:
        notebook_id: ID of the notebook to query
        query: Question to ask

    Returns:
        AI-generated response from NotebookLM
    """
    try:
        async with NotebookLMBrowser(headless=get_headless_mode()) as browser:
            # Check authentication
            is_authenticated = await browser.check_authentication()
            if not is_authenticated:
                raise AuthenticationError(
                    "Not authenticated. Run: python scripts/setup_auth.py"
                )

            # Navigate to notebook
            notebook_url = f"https://notebooklm.google.com/notebook/{notebook_id}"
            await browser.goto(notebook_url)
            await browser.page.wait_for_timeout(2000)

            # Find chat input
            chat_input = await find_element(
                browser.page,
                Selectors.CHAT_INPUT,
                timeout=10000
            )

            # Type query
            await chat_input.fill(query)

            # Submit query
            try:
                submit_button = await find_element(
                    browser.page,
                    Selectors.CHAT_SUBMIT,
                    timeout=3000
                )
                await submit_button.click()
            except PlaywrightTimeoutError:
                # Fallback: press Enter
                await chat_input.press("Enter")

            # Wait for thinking message to appear (indicates query is being processed)
            await browser.page.wait_for_timeout(1000)

            # Wait for loading/thinking to complete (AI generates response)
            try:
                # Wait for thinking message to disappear (indicates response is ready)
                await browser.page.wait_for_selector(
                    '.thinking-message',
                    state="hidden",
                    timeout=45000  # Increased timeout for complex queries
                )
            except PlaywrightTimeoutError:
                # If no thinking message detected, try other loading indicators
                try:
                    await browser.page.wait_for_selector(
                        ', '.join(Selectors.LOADING_INDICATOR[1:]),  # Skip .thinking-message
                        state="hidden",
                        timeout=10000
                    )
                except PlaywrightTimeoutError:
                    # Continue even if we don't detect loading indicator
                    pass

            # Additional wait for response to fully render
            await browser.page.wait_for_timeout(2000)

            # Get the latest response
            response_elements = await find_all_elements(
                browser.page,
                Selectors.CHAT_RESPONSE,
                timeout=10000
            )

            if not response_elements:
                raise RuntimeError("No response received from NotebookLM")

            # Get the last response (most recent)
            last_response = response_elements[-1]
            response_text = await last_response.inner_text()

            return response_text.strip()

    except AuthenticationError:
        raise
    except PlaywrightTimeoutError as e:
        raise RuntimeError(f"NotebookLM UI timed out: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to query notebook: {str(e)}")


# ============================================================================
# PHASE 2 TOOLS - Advanced Features
# ============================================================================

@mcp.tool()
async def generate_study_guide(
    notebook_id: str = Field(description="Notebook ID to generate study guide for"),
    guide_type: Literal["faq", "briefing_doc", "table_of_contents"] = Field(
        description="Type of study guide to generate"
    )
) -> Dict[str, str]:
    """
    Generate a study guide from notebook sources.

    Args:
        notebook_id: ID of the notebook
        guide_type: Type of guide (faq, briefing_doc, or table_of_contents)

    Returns:
        Status and guide information
    """
    try:
        async with NotebookLMBrowser(headless=get_headless_mode()) as browser:
            # Check authentication
            is_authenticated = await browser.check_authentication()
            if not is_authenticated:
                raise AuthenticationError(
                    "Not authenticated. Run: python scripts/setup_auth.py"
                )

            # Navigate to notebook
            notebook_url = f"https://notebooklm.google.com/notebook/{notebook_id}"
            await browser.goto(notebook_url)
            await browser.page.wait_for_timeout(2000)

            # Click generate study guide button
            guide_button = await find_element(
                browser.page,
                Selectors.GENERATE_GUIDE_BUTTON,
                timeout=10000
            )
            await guide_button.click()
            await browser.page.wait_for_timeout(1000)

            # Select guide type
            if guide_type == "faq":
                type_button = await find_element(
                    browser.page,
                    Selectors.STUDY_GUIDE_TYPE_FAQ
                )
                await type_button.click()
            elif guide_type == "briefing_doc":
                type_button = await find_element(
                    browser.page,
                    Selectors.STUDY_GUIDE_TYPE_BRIEFING
                )
                await type_button.click()
            elif guide_type == "table_of_contents":
                type_button = await find_element(
                    browser.page,
                    Selectors.STUDY_GUIDE_TYPE_TOC
                )
                await type_button.click()

            # Wait for guide to be generated
            await browser.page.wait_for_timeout(5000)

            return {
                "status": "success",
                "message": f"Generated {guide_type} study guide",
                "notebook_id": notebook_id,
                "guide_type": guide_type
            }

    except AuthenticationError:
        raise
    except PlaywrightTimeoutError as e:
        raise RuntimeError(f"NotebookLM UI timed out: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to generate study guide: {str(e)}")


@mcp.tool()
async def generate_audio_overview(
    notebook_id: str = Field(description="Notebook ID to generate audio overview for")
) -> Dict[str, str]:
    """
    Generate an audio overview (podcast) from notebook sources.

    Note: This is an async operation in NotebookLM. The audio may take
    several minutes to generate and will not be immediately available.

    Args:
        notebook_id: ID of the notebook

    Returns:
        Status message
    """
    try:
        async with NotebookLMBrowser(headless=get_headless_mode()) as browser:
            # Check authentication
            is_authenticated = await browser.check_authentication()
            if not is_authenticated:
                raise AuthenticationError(
                    "Not authenticated. Run: python scripts/setup_auth.py"
                )

            # Navigate to notebook
            notebook_url = f"https://notebooklm.google.com/notebook/{notebook_id}"
            await browser.goto(notebook_url)
            await browser.page.wait_for_timeout(2000)

            # Click generate audio button
            audio_button = await find_element(
                browser.page,
                Selectors.GENERATE_AUDIO_BUTTON,
                timeout=10000
            )
            await audio_button.click()

            # Wait for generation to start
            await browser.page.wait_for_timeout(3000)

            return {
                "status": "success",
                "message": "Audio overview generation started",
                "notebook_id": notebook_id,
                "note": "Audio generation is async and may take several minutes"
            }

    except AuthenticationError:
        raise
    except PlaywrightTimeoutError as e:
        raise RuntimeError(f"NotebookLM UI timed out: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to generate audio overview: {str(e)}")


@mcp.tool()
async def get_notebook_sources(
    notebook_id: str = Field(description="Notebook ID to get sources from")
) -> List[Dict[str, str]]:
    """
    Get list of sources in a notebook.

    Args:
        notebook_id: ID of the notebook

    Returns:
        List of sources with their titles and types
    """
    try:
        async with NotebookLMBrowser(headless=get_headless_mode()) as browser:
            # Check authentication
            is_authenticated = await browser.check_authentication()
            if not is_authenticated:
                raise AuthenticationError(
                    "Not authenticated. Run: python scripts/setup_auth.py"
                )

            # Navigate to notebook
            notebook_url = f"https://notebooklm.google.com/notebook/{notebook_id}"
            await browser.goto(notebook_url)
            await browser.page.wait_for_timeout(2000)

            # Find source list elements
            source_elements = await find_all_elements(
                browser.page,
                Selectors.SOURCES_LIST,
                timeout=10000
            )

            if not source_elements:
                return []

            sources = []
            for idx, element in enumerate(source_elements):
                try:
                    # Extract source title/name
                    title = await element.inner_text()

                    sources.append({
                        "index": str(idx + 1),
                        "title": title.strip()[:100],  # Truncate long titles
                    })
                except Exception:
                    continue

            return sources

    except AuthenticationError:
        raise
    except PlaywrightTimeoutError as e:
        raise RuntimeError(f"NotebookLM UI timed out: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to get notebook sources: {str(e)}")


# ============================================================================
# Health Check Endpoints
# ============================================================================

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for Kubernetes probes."""
    from starlette.responses import JSONResponse
    return JSONResponse({
        "status": "healthy",
        "transport": os.getenv("MCP_TRANSPORT", "stdio"),
        "headless": get_headless_mode()
    })

@mcp.custom_route("/readiness", methods=["GET"])
async def readiness_check(request):
    """Readiness probe - checks if browser can be initialized."""
    from starlette.responses import JSONResponse
    try:
        from playwright.async_api import async_playwright
        return JSONResponse({"status": "ready", "playwright": "available"})
    except Exception as e:
        return JSONResponse(
            {"status": "not_ready", "error": str(e)},
            status_code=503
        )


# ============================================================================
# Entry point
# ============================================================================

def main():
    """Run the MCP server with configurable transport."""
    import os

    # Get transport mode from environment
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()

    if transport == "streamable-http":
        # HTTP mode for Kubernetes/OpenShift
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8080"))

        print(f"Starting MCP server in HTTP mode on {host}:{port}")
        mcp.run(
            transport="streamable-http",
            host=host,
            port=port
        )
    else:
        # stdio mode for Claude Desktop (default)
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
