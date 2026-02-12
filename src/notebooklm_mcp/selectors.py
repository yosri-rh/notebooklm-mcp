"""
UI selectors for NotebookLM interface.

NOTE: NotebookLM uses obfuscated class names that change frequently.
These selectors use multiple fallback strategies for resilience.
Update these after inspecting the actual NotebookLM UI.
"""

from typing import List


class Selectors:
    """Container for NotebookLM UI selectors with fallback strategies."""

    # Notebook list/grid view
    # NOTE: NotebookLM now uses a table view instead of cards
    # Use 'tr[mat-row]' to get table rows, then click to navigate
    NOTEBOOK_LIST: List[str] = [
        'tr[mat-row]',  # Table rows (current implementation)
        '[data-testid="notebook-card"]',  # Legacy: card view
        '[aria-label*="notebook" i][role="button"]',
        'a[href*="/notebook/"]',
        'div[role="listitem"]',
    ]

    # Table view selectors (current NotebookLM UI)
    NOTEBOOK_TABLE_ROW: List[str] = ['tr[mat-row]']
    NOTEBOOK_TABLE_TITLE: List[str] = ['td.title-column .project-table-title']

    # Individual notebook card elements
    NOTEBOOK_TITLE: List[str] = [
        '[data-testid="notebook-title"]',
        'h2',
        'h3',
        '[role="heading"]',
    ]

    # Create new notebook button
    CREATE_NOTEBOOK_BUTTON: List[str] = [
        '[aria-label*="create" i][aria-label*="notebook" i]',
        'button:has-text("Create")',
        '[data-testid="create-notebook"]',
    ]

    # Notebook name input (when creating)
    NOTEBOOK_NAME_INPUT: List[str] = [
        '[aria-label*="name" i][type="text"]',
        'input[placeholder*="name" i]',
        '[data-testid="notebook-name-input"]',
    ]

    # Add source button/dialog
    ADD_SOURCE_BUTTON: List[str] = [
        '[aria-label*="add" i][aria-label*="source" i]',
        'button:has-text("Add")',
        '[data-testid="add-source"]',
        '[aria-label*="upload" i]',
    ]

    # Source type selectors
    SOURCE_TYPE_URL: List[str] = [
        '[aria-label*="website" i]',
        'button:has-text("Website")',
        '[data-testid="source-type-url"]',
    ]

    SOURCE_TYPE_TEXT: List[str] = [
        '[aria-label*="text" i]',
        'button:has-text("Text")',
        '[data-testid="source-type-text"]',
    ]

    SOURCE_TYPE_YOUTUBE: List[str] = [
        '[aria-label*="youtube" i]',
        'button:has-text("YouTube")',
        '[data-testid="source-type-youtube"]',
    ]

    # Source input fields
    SOURCE_URL_INPUT: List[str] = [
        'input[type="url"]',
        'input[placeholder*="url" i]',
        '[aria-label*="url" i]',
    ]

    SOURCE_TEXT_INPUT: List[str] = [
        'textarea',
        '[aria-label*="text" i][role="textbox"]',
        '[contenteditable="true"]',
    ]

    # Chat/Query interface
    CHAT_INPUT: List[str] = [
        'textarea[aria-label*="query" i]',  # Current: aria-label="Query box"
        'textarea[placeholder*="start typing" i]',  # Current: placeholder="Start typing..."
        'textarea',  # Fallback: generic textarea (notebook pages typically have only one)
        'textarea[placeholder*="ask" i]',  # Legacy
        'textarea[aria-label*="ask" i]',  # Legacy
        '[data-testid="chat-input"]',  # Legacy
        'textarea[placeholder*="question" i]',  # Legacy
    ]

    CHAT_SUBMIT: List[str] = [
        '[aria-label*="send" i]',
        'button[type="submit"]',
        '[data-testid="send-message"]',
    ]

    CHAT_RESPONSE: List[str] = [
        '.to-user-message-card-content .message-text-content',  # Current: AI response text content
        '.to-user-message-inner-content',  # Current: Alternative AI response container
        'div[class*="to-user-message"]',  # Current: AI message cards
        '[data-testid="chat-message"]',  # Legacy
        '[role="article"]',  # Legacy
        'div[class*="message"]',  # Legacy fallback
    ]

    # Study guide/document generation
    GENERATE_GUIDE_BUTTON: List[str] = [
        '[aria-label*="study guide" i]',
        'button:has-text("Study guide")',
        '[data-testid="generate-study-guide"]',
    ]

    STUDY_GUIDE_TYPE_FAQ: List[str] = [
        'button:has-text("FAQ")',
        '[aria-label*="faq" i]',
    ]

    STUDY_GUIDE_TYPE_BRIEFING: List[str] = [
        'button:has-text("Briefing")',
        '[aria-label*="briefing" i]',
    ]

    STUDY_GUIDE_TYPE_TOC: List[str] = [
        'button:has-text("Table of contents")',
        '[aria-label*="table of contents" i]',
    ]

    # Audio overview (podcast)
    GENERATE_AUDIO_BUTTON: List[str] = [
        '[aria-label*="audio" i]',
        'button:has-text("Audio overview")',
        '[data-testid="generate-audio"]',
    ]

    # Sources list
    SOURCES_LIST: List[str] = [
        '[data-testid="source-item"]',
        '[aria-label*="source" i][role="listitem"]',
        'li[class*="source"]',
    ]

    # Common UI elements
    LOADING_INDICATOR: List[str] = [
        '.thinking-message',  # Current: "Assessing relevance..." message
        '[aria-label*="loading" i]',
        '[role="progressbar"]',
        'div[class*="loading"]',
        'div[class*="spinner"]',
    ]

    SUBMIT_BUTTON: List[str] = [
        'button[type="submit"]',
        'button:has-text("Submit")',
        'button:has-text("Add")',
        'button:has-text("Create")',
    ]


async def find_element(page, selectors: List[str], timeout: int = 5000):
    """
    Try multiple selectors in order until one succeeds.

    Args:
        page: Playwright page object
        selectors: List of CSS selectors to try
        timeout: Timeout per selector in milliseconds

    Returns:
        First matching element

    Raises:
        TimeoutError: If no selector matches
    """
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError

    for selector in selectors:
        try:
            element = await page.wait_for_selector(selector, timeout=timeout)
            return element
        except PlaywrightTimeoutError:
            continue

    raise PlaywrightTimeoutError(
        f"None of the selectors matched: {selectors[:3]}..."
    )


async def find_all_elements(page, selectors: List[str], timeout: int = 5000):
    """
    Try multiple selectors and return all matching elements.

    Args:
        page: Playwright page object
        selectors: List of CSS selectors to try
        timeout: Timeout per selector in milliseconds

    Returns:
        List of matching elements
    """
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError

    for selector in selectors:
        try:
            await page.wait_for_selector(selector, timeout=timeout)
            elements = await page.query_selector_all(selector)
            if elements:
                return elements
        except PlaywrightTimeoutError:
            continue

    return []
