import asyncio
import time

from playwright.async_api import async_playwright


async def extract_input_fields(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=True if you don’t want UI
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        time.sleep(50)

        # Select all possible inputtable fields
        selectors = (
            "input:not([type='hidden']):not([type='submit']):not([type='button']), "
            "textarea, select, [contenteditable='true'], [role='textbox']"
        )
        elements = await page.query_selector_all(selectors)

        fillable = []
        for el in elements:
            try:
                tag = await el.evaluate("e => e.tagName.toLowerCase()")
                type_ = await el.get_attribute("type")
                name = await el.get_attribute("name")
                id_ = await el.get_attribute("id")
                placeholder = await el.get_attribute("placeholder")
                aria_label = await el.get_attribute("aria-label")
                label_text = await page.evaluate(
                    """el => {
                        let label = el.labels ? Array.from(el.labels).map(l => l.innerText).join(', ') : '';
                        if (!label) {
                            const id = el.id;
                            if (id) {
                                const l = document.querySelector(`label[for="${id}"]`);
                                if (l) label = l.innerText;
                            }
                        }
                        return label;
                    }""",
                    el,
                )

                is_visible = await el.is_visible()
                box = await el.bounding_box()
                value = await el.evaluate("e => e.value || ''")

                fillable.append(
                    {
                        "tag": tag,
                        "type": type_,
                        "id": id_,
                        "name": name,
                        "placeholder": placeholder,
                        "aria_label": aria_label,
                        "label": label_text.strip() if label_text else None,
                        "visible": is_visible,
                        "has_box": bool(box),
                        "current_value": value.strip(),
                    }
                )
            except Exception:
                continue

        await browser.close()
        return fillable


async def main():
    url = "https://google.com"  # Change this to your target
    results = await extract_input_fields(url)
    print(f"Total fillable fields found: {len(results)}\n")
    for i, r in enumerate(results, 1):
        print(
            f"{i}. <{r['tag']}> | type={r['type']} | id={r['id']} | name={r['name']} "
            f"| placeholder={r['placeholder']} | label={r['label']}"
        )


if __name__ == "__main__":
    asyncio.run(main())


"""
<textarea 
    jsname="yZiJbe" 
    class="gLFyf" 
    aria-controls="Alh6id" 
    aria-owns="Alh6id" 
    autofocus="" 
    title="Search" 
    value="" 
    aria-label="Search" 
    placeholder="" 
    aria-autocomplete="both" 
    aria-expanded="false" 
    aria-haspopup="false" 
    autocapitalize="off" 
    autocomplete="off" 
    autocorrect="off" 
    id="APjFqb" 
    maxlength="2048" 
    name="q" 
    role="combobox" 
    rows="1" 
    spellcheck="false" 
    data-ved="0ahUKEwjL3e3lkKeQAxVrUGwGHeKBHaMQ39UDCAU">
</textarea>
"""
