import math
from collections import Counter
from urllib.parse import urlparse

from playwright.async_api import Page

from pyba.utils.structure import CleanedDOM


def url_entropy(url) -> int:
    """
    Computes the shannon entropy of a URL useful for determining which URLs to
    keep during the general DOM href extraction
    """
    counts = Counter(url)
    total = len(url)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def is_absolute_url(url: str) -> bool:
    """
    Determines if a URL is absolute or relative. Used in fixing relative URLs
    in case of goto actions in playwright
    """
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


async def initial_page_setup(page: Page) -> CleanedDOM:
    """
    Helper function for main: goto for the initial page -> Optimisation
    """
    start_page = "https://search.brave.com"

    await page.goto(start_page)

    cleaned_dom = CleanedDOM(
        hyperlinks=[],
        input_fields=["#searchbox"],
        clickable_fields=[],
        actual_text=None,
        current_url=start_page,
    )

    return cleaned_dom
