from typing import List, Dict
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def extract_clickables(html: str, base_url: str = None) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")

    candidates = []
    # obvious interactive tags
    for tag in soup.find_all(["a", "button", "area", "summary"]):
        if tag.name == "a" and not tag.get("href"):
            # <a> without href may still be clickable (JS) so keep it
            pass
        candidates.append(tag)

    # inputs that act like buttons
    for tag in soup.find_all("input"):
        t = tag.get("type", "").lower()
        if t in ("button", "submit", "reset"):
            candidates.append(tag)

    # any element with onclick attribute
    candidates += soup.find_all(attrs={"onclick": True})

    # any element with role=button or role=link
    candidates += soup.find_all(attrs={"role": lambda v: v and v.lower() in ("button", "link")})

    # any element with a tabindex (keyboard-focusable)
    candidates += soup.find_all(attrs={"tabindex": True})

    # dedupe and build results
    seen = set()
    results = []
    for el in candidates:
        # simple de-dup key
        key = (el.name, str(el))
        if key in seen:
            continue
        seen.add(key)

        href = el.get("href")
        onclick = el.get("onclick")
        role = el.get("role")
        tabindex = el.get("tabindex")
        text = el.get_text(strip=True)

        # make href absolute if base_url provided
        if href and base_url:
            href = urljoin(base_url, href)

        results.append(
            {
                "tag": el.name,
                "text": text,
                "href": href,
                "onclick": onclick,
                "role": role,
                "tabindex": tabindex,
                "outer_html": str(el)[:1000],  # truncated; remove slicing if you want full
            }
        )

    return results


# Example usage:
if __name__ == "__main__":
    html = open("output.html", "r", encoding="utf-8").read()  # or use your html string
    clickables = extract_clickables(html, base_url="https://google.com")
    for c in clickables:
        print(
            c["tag"],
            "|",
            c["text"] or "<no-text>",
            "|",
            c["href"] or c["onclick"] or c["role"] or c["tabindex"],
        )
