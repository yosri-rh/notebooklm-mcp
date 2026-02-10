"""NotebookLM MCP Server - Browser automation for Google NotebookLM."""

__version__ = "0.1.0"

from .server import mcp, main
from .browser import NotebookLMBrowser, AuthenticationError

__all__ = ["mcp", "main", "NotebookLMBrowser", "AuthenticationError"]
