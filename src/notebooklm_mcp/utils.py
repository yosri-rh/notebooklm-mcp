"""Utility functions for NotebookLM MCP server."""
import logging
from typing import Optional


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up logging for the MCP server.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger
    """
    logger = logging.getLogger("notebooklm-mcp")
    logger.setLevel(getattr(logging, level.upper()))

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def extract_notebook_id(url: str) -> Optional[str]:
    """
    Extract notebook ID from NotebookLM URL.

    Args:
        url: NotebookLM URL

    Returns:
        Notebook ID if found, None otherwise
    """
    if "/notebook/" in url:
        return url.split("/notebook/")[-1].split("?")[0].split("#")[0]
    return None


def validate_notebook_id(notebook_id: str) -> bool:
    """
    Validate notebook ID format.

    Args:
        notebook_id: Notebook ID to validate

    Returns:
        True if valid, False otherwise
    """
    # Basic validation - NotebookLM IDs are typically alphanumeric
    if not notebook_id:
        return False
    return len(notebook_id) > 0 and not any(c in notebook_id for c in ["?", "#", "/"])
