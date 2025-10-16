import asyncio

from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError


async def extract_all_text(url: str):
    """
    Navigates to a URL and extracts all visible text content from the page body.

    This function launches a headless browser, goes to the specified URL,
    and then retrieves the text from the body of the page. It processes
    the text to provide a clean list of non-empty lines.

    Args:
        url: The URL of the webpage from which to extract text.

    Returns:
        A list of strings, where each string is a line of text from the page.
        Returns an empty list if the page fails to load.
    """
    print(f"Attempting to extract text from: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except PlaywrightTimeoutError:
            print(f"❌ Timed out loading {url}")
            await browser.close()
            return []

        # 'page.inner_text("body")' is an effective way to get all visible text
        # content, similar to what a user would see.
        body_text = await page.inner_text("body")

        # Split the text by newlines to get a list of text blocks/lines.
        lines = body_text.split("\n")

        # Clean up the list by removing leading/trailing whitespace from each line
        # and filtering out any lines that are empty after stripping.
        non_empty_lines = [line.strip() for line in lines if line.strip()]

        await browser.close()

        print(f"✅ Successfully extracted {len(non_empty_lines)} lines of text.")
        return non_empty_lines


async def main():
    """
    Main function to run the text extraction script on a sample URL.
    """
    url_to_scrape = "https://google.com"
    extracted_text = await extract_all_text(url_to_scrape)

    if extracted_text:
        print("\n--- Extracted Text ---")
        for i, line in enumerate(extracted_text, 1):
            print(f"{line}")
        print("\n--- End of Report ---")


if __name__ == "__main__":
    asyncio.run(main())
