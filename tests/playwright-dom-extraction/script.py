"""
Here's the plan:

1. Extract the DOM from the link
2. Extract all the hyperlinks from it
3. Extract all input_fields from it (basically all fillable boxes)
4. Extract all the clickables from it
5. Extract all the actual text from it (we don't have to do any OCR for this!)

Pass that into a nice structured JSON and give it to the model instead of the raw shit.
"""

import asyncio
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError


def _extract_clickables(html: str, base_url: str = None):
    soup = BeautifulSoup(html, "html.parser")
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


def _extract_href(dom):
    soup = BeautifulSoup(str(dom), "html.parser")
    hrefs = [a["href"] for a in soup.find_all("a", href=True)]
    return hrefs


async def _extract_all_text(body_text: str):
    lines = body_text.split("\n")
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return non_empty_lines


async def _extract_input_fields(elements, test_value="hello world"):
    valid_fields = []
    for i, el in enumerate(elements, start=1):
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
            await el.fill(test_value, timeout=2000)
            value = (
                await el.input_value()
                if field_info["tag"] in ["input", "textarea", "select"]
                else await el.inner_text()
            )

            if test_value in value:
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


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            base_url = "https://www.google.com"
            await page.goto(base_url, timeout=30000)
            await page.wait_for_timeout(2000)

            dom = await page.content()
            body_text = await page.inner_text("body")

            selectors = (
                "input:not([type='hidden']):not([type='submit']):not([type='button']):not([type='reset']):not([type='file'])",
                "textarea",
                "select",
                "[contenteditable='true']",
                "[role='textbox']",
                "[role='searchbox']",
                "[role='combobox']",
            )
            combined_selector = ", ".join(selectors)
            elements = await page.query_selector_all(combined_selector)

            hrefs = _extract_href(dom)
            all_text = await _extract_all_text(body_text)
            fillable_selectors = await _extract_input_fields(elements)
            # get_clickables = _extract_clickables(html=dom, base_url=base_url)

            output = {
                "hyperlinks": hrefs,
                "text": all_text,
                "fillable_selectors": fillable_selectors,
                # "clickables": get_clickables,
            }

            return output

        except Exception as e:
            print("Error:", e)
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    output = asyncio.run(main())
    print(output)
