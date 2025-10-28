import math
from collections import Counter
from urllib.parse import urlparse


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
