import asyncio

from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError


async def extract_and_test_fillable_fields(url: str, test_value="hello world"):
    """
    Asynchronously navigates to a URL, identifies all potential fillable fields,
    tests them for input, and returns a list of fields that can be filled.

    This optimized version directly interacts with element handles instead of
    re-querying the DOM with selectors, significantly improving performance.

    Args:
        url: The URL of the webpage to test.
        test_value: The string value to use for testing input fields.

    Returns:
        A list of dictionaries, where each dictionary represents a valid,
        fillable field and contains its properties and a recommended selector.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Changed to headless for speed
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except PlaywrightTimeoutError:
            print(f"❌ Timed out loading {url}")
            await browser.close()
            return []

        # Use a comprehensive selector to find all potential input elements.
        # This includes standard inputs, textareas, content-editable elements,
        # and elements with common testing attributes.
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

        print(f"\n🔍 Found {len(elements)} potential fillable elements on {url}\n")

        valid_fields = []
        for i, el in enumerate(elements, start=1):
            is_visible = await el.is_visible()
            is_enabled = await el.is_enabled()

            # --- OPTIMIZATION: Skip non-interactive elements early ---
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
            print(
                f"{i}. Testing <{field_info['tag']}> name={field_info['name']!r} id={field_info['id']!r}"
            )

            try:
                # --- OPTIMIZATION: Use the element handle directly with a timeout ---
                # This avoids slow, repeated DOM lookups with page.fill(selector)
                await el.fill(test_value, timeout=2000)

                # Verify that the fill was successful
                value = (
                    await el.input_value()
                    if field_info["tag"] in ["input", "textarea", "select"]
                    else await el.inner_text()
                )

                if test_value in value:
                    # --- OPTIMIZATION: Build a single, high-quality selector for reporting ---
                    # We are not using this to interact, just to inform the user.
                    if field_info["id"]:
                        field_info["selector"] = f"#{field_info['id']}"
                    elif field_info["name"]:
                        field_info[
                            "selector"
                        ] = f"[{field_info['tag']}[name='{field_info['name']}']"
                    elif field_info["placeholder"]:
                        field_info[
                            "selector"
                        ] = f"[{field_info['tag']}[placeholder='{field_info['placeholder']}']"
                    else:
                        # Fallback for elements without common attributes
                        field_info["selector"] = f"{field_info['tag']} (no unique attribute found)"

                    print(f"   ✅ Successfully filled. Best selector: {field_info['selector']}")
                    valid_fields.append(field_info)
                else:
                    print("   ⚠️  Field did not retain the test value.")

            except PlaywrightTimeoutError:
                print("   ❌ Timed out trying to fill this element.")
            except Exception as e:
                # This can happen if the element is not an input element (e.g., contenteditable div)
                # or becomes detached from the DOM during the test.
                print(f"   ⚠️  Could not fill. Reason: {str(e).splitlines()[0]}")

        await browser.close()

        print("\n--- Summary ---")
        print(f"✅ Found {len(valid_fields)} truly fillable fields.\n")
        if valid_fields:
            print("Recommended selectors for fillable fields:")
            for v in valid_fields:
                print(
                    f"→ Tag: <{v['tag']}>, Type: {v['type'] or 'N/A'}, Selector: {v['selector']}"
                )
        print("--- End of Report ---\n")

        return valid_fields


async def main():
    # Test with a few different URLs
    urls_to_test = ["https://www.google.com", "https://github.com/login", "https://duckduckgo.com"]
    for url in urls_to_test:
        await extract_and_test_fillable_fields(url)


if __name__ == "__main__":
    asyncio.run(main())
