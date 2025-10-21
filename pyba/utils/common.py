import math
from collections import Counter


def url_entropy(url):
    counts = Counter(url)
    total = len(url)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())
