from typing import Any, Callable, Optional, Union
import aiohttp
from dataclasses import dataclass
from bs4 import BeautifulSoup

@dataclass
class WebPage:
    """A class to represent a web page."""
    url: str
    inner_text: str
    html: str

class WebBrowserEngine:
    """A class to handle web browsing and content extraction."""

    def __init__(self, proxy: Optional[str] = None, browse_func: Optional[Callable] = None):
        """Initialize the web browser engine.

        Args:
            proxy: Optional proxy URL.
            browse_func: Optional custom browse function.
        """
        self.proxy = proxy
        self.browse_func = browse_func
        self.session = None

    @classmethod
    def from_browser_config(cls, config: dict, browse_func: Optional[Callable] = None, proxy: Optional[str] = None) -> 'WebBrowserEngine':
        """Create a web browser engine from a configuration.

        Args:
            config: The browser configuration.
            browse_func: Optional custom browse function.
            proxy: Optional proxy URL.

        Returns:
            A WebBrowserEngine instance.
        """
        return cls(proxy=proxy, browse_func=browse_func)

    async def run(self, url: str, *urls: str, per_page_timeout: Optional[float] = None) -> Union[WebPage, list[WebPage]]:
        """Run the web browser to fetch content from URLs.

        Args:
            url: The main URL to fetch.
            urls: Additional URLs to fetch.
            per_page_timeout: Optional timeout per page in seconds.

        Returns:
            A WebPage object or list of WebPage objects.
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        if self.browse_func:
            return await self.browse_func(url, *urls)

        all_urls = [url] + list(urls)
        pages = []
        
        for url in all_urls:
            try:
                async with self.session.get(url, proxy=self.proxy, timeout=per_page_timeout) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        # Get text
                        text = soup.get_text()
                        # Break into lines and remove leading and trailing space on each
                        lines = (line.strip() for line in text.splitlines())
                        # Break multi-headlines into a line each
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        # Drop blank lines
                        text = '\n'.join(chunk for chunk in chunks if chunk)
                        pages.append(WebPage(url=url, inner_text=text, html=html))
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                pages.append(WebPage(url=url, inner_text="Fail to load page", html=""))

        return pages[0] if not urls else pages

    async def close(self):
        """Close the web browser session."""
        if self.session:
            await self.session.close()
            self.session = None 