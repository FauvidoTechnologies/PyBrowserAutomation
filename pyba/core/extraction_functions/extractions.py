import asyncio
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from typing import List

class DOMExtraction:
    """
    Given the DOM from the URL, this class provides functions to extract it properly
    
    1. Extract all the hyperlinks from it
    2. Extract all input_fields from it (basically all fillable boxes)
    3. Extract all the clickables from it
    4. Extract all the actual text from it (we don't have to do any OCR for this!)

    Note that extracing all clickable elements might get messy so we'll use that only when
    the total length is lower than a certain threshold.
    """

    def __init__(self, html: str, body_text: str, elements: str, base_url: str = None) -> None:
        """
        We'll take the entire dom, the text_body and the elements for sure 
        """

        self.html = html
        self.body_text = body_text
        self.elements = elements
        self.base_url = base_url

        # For testing fields
        self.test_value = "PyBA"

    def _extract_clickables(self) -> List:
        soup = BeautifulSoup(self.html, "html.parser")
        candidates = []
        for tag in soup.find_all(["a", "button", "area", "summary"]):
            if tag.name == "a" and not tag.get("href"):
                pass
            candidates.append(tag)

        for tag in soup.find_all("input"):
            t = tag.get("type", "").lower()
            if t in ("button", "submit", "reset"):
                candidates.append(tag)

        candidates += soup.find_all(attrs={"onclick": True})
        candidates += soup.find_all(attrs={"role": lambda v: v and v.lower() in ("button", "link")})
        candidates += soup.find_all(attrs={"tabindex": True})

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
                    "outer_html": str(el)[:1000],
                }
            )

        return results


    def _extract_href(self) -> List:
        soup = BeautifulSoup(str(dom), "html.parser")
        hrefs = [a["href"] for a in soup.find_all("a", href=True)]
        return hrefs


    async def _extract_all_text(self) -> List:
        lines = body_text.split("\n")
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        return non_empty_lines


    async def _extract_input_fields(self) -> List:
        valid_fields = []
        for i, el in enumerate(self.elements, start=1):
            is_visible = await el.is_visible()
            is_enabled = await el.is_enabled()

            if not is_visible or not is_enabled:
                continue

            field_info = {
                "tag": await el.evaluate("e => e.tagName.toLowerCase()"),
                "type": await el.get_attribute("type"),
                "id": await el.get_attribute("id"),
                "name": await el.get_attribute("name"),
                "placeholder": await el.get_attribute("placeholder"),
                "aria_label": await el.get_attribute("aria-label"),
                "selector": None,
            }

            try:
                await el.fill(self.test_value, timeout=2000)
                value = (
                    await el.input_value()
                    if field_info["tag"] in ["input", "textarea", "select"]
                    else await el.inner_text()
                )

                if self.test_value in value:
                    if field_info["id"]:
                        field_info["selector"] = f"#{field_info['id']}"
                    elif field_info["name"]:
                        field_info["selector"] = f"[{field_info['tag']}[name='{field_info['name']}']"
                    elif field_info["placeholder"]:
                        field_info[
                            "selector"
                        ] = f"[{field_info['tag']}[placeholder='{field_info['placeholder']}']"
                    else:
                        field_info["selector"] = f"{field_info['tag']} (no unique attribute found)"
                    valid_fields.append(field_info)
                else:
                    pass
            except PlaywrightTimeoutError:
                pass
            except Exception:
                pass

        return valid_fields
