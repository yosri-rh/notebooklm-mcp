"""Browser automation manager for NotebookLM."""
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError


class AuthenticationError(Exception):
    """Raised when authentication is required or has expired."""
    pass


class NotebookLMBrowser:
    """Manages Playwright browser context for NotebookLM automation."""

    def __init__(
        self,
        headless: bool = True,
        user_data_dir: Optional[str] = None,
        timeout: int = 30000
    ):
        """
        Initialize browser manager.

        Args:
            headless: Run browser in headless mode
            user_data_dir: Path to persistent Chrome profile
            timeout: Default timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout

        if user_data_dir:
            self.user_data_dir = Path(user_data_dir)
        else:
            # Default to chrome-user-data in project root
            self.user_data_dir = Path(__file__).parent.parent.parent / "chrome-user-data"

        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Start browser context."""
        self.playwright = await async_playwright().start()

        # Launch persistent context to maintain authentication
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
            ],
            viewport={'width': 1920, 'height': 1080},
        )

        # Set default timeout
        self.context.set_default_timeout(self.timeout)

        # Create new page
        self.page = await self.context.new_page()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up browser context."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()

    async def goto(self, url: str, wait_until: str = "networkidle") -> None:
        """
        Navigate to URL.

        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete
        """
        if not self.page:
            raise RuntimeError("Browser not initialized. Use 'async with' context manager.")

        try:
            await self.page.goto(url, wait_until=wait_until)
        except PlaywrightTimeoutError:
            # Try again with less strict wait condition
            await self.page.goto(url, wait_until="domcontentloaded")

    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        Wait for selector to appear.

        Args:
            selector: CSS selector to wait for
            timeout: Optional timeout override in milliseconds
        """
        if not self.page:
            raise RuntimeError("Browser not initialized. Use 'async with' context manager.")

        await self.page.wait_for_selector(selector, timeout=timeout or self.timeout)

    async def check_authentication(self) -> bool:
        """
        Check if user is authenticated to NotebookLM.

        Returns:
            True if authenticated, False otherwise
        """
        if not self.page:
            raise RuntimeError("Browser not initialized. Use 'async with' context manager.")

        try:
            await self.goto("https://notebooklm.google.com")

            # Wait a bit for potential redirects
            await self.page.wait_for_timeout(2000)

            # Check if we're on the login page
            current_url = self.page.url
            if "accounts.google.com" in current_url:
                return False

            # Check for NotebookLM UI elements (will be refined after UI inspection)
            try:
                await self.page.wait_for_selector('[aria-label*="notebook" i], [data-testid], .notebook', timeout=5000)
                return True
            except PlaywrightTimeoutError:
                return False

        except Exception:
            return False
