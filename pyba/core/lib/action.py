import asyncio
from urllib.parse import urljoin

from playwright._impl._errors import Error
from playwright.async_api import Page

from pyba.utils.common import is_absolute_url
from pyba.utils.structure import PlaywrightAction


class PlaywrightActionPerformer:
    """
    The playwright automation class. To add new handles, make a function here
    and define that under perform()

    Below is an exhaustive set of playwright actions that the handler will manage and the dispatcher will execute

    1. Navigation functions
        - handle_navigation
        - handle_back
        - handle_forward
        - handle_reload

    2. Interaction functions
        - handle_input
        - handle_typing
        - handle_click
        - handle_double_click
        - handle_hover
        - handle_checkboxes
        - handle_select
        - handle_file_upload

    3. Keyboard/mouse functions
        - handle_press
        - handle_keyboard_press
        - handle_keyboard_type
        - handle_mouse_move
        - handle_mouse_click

    4. Scrolling
        - handle_scrolling

    5. Waits
        - handle_wait

    6. Javascript functions
        - handle_evaluate_js
        - handle_screenshot
        - handle_download

    7. New pages
        - handle_switch_page
        - handle_new_page
        - handle_close_page

    """

    def __init__(self, page: Page, action: PlaywrightAction):
        self.page = page
        self.action = action

    # -----------------
    # Handle nagivation
    # -----------------
    async def handle_navigation(self):
        """
        Handle's browser naviation -> Opening new websites
        Wait's until the page is loaded
        """
        await self.page.goto(self.action.goto)
        await self.page.wait_for_load_state("domcontentloaded")

    async def handle_back(self):
        await self.page.go_back(wait_until="domcontentloaded")

    async def handle_forward(self):
        await self.page.go_forward(wait_until="domcontentloaded")

    async def handle_reload(self):
        await self.page.reload(wait_until="domcontentloaded")

    # -------------------
    # Handle interactions
    # -------------------
    async def handle_input(self):
        """
        Inputs a value to a selector field
        """
        await self.page.fill(self.action.fill_selector, self.action.fill_value)

    async def handle_typing(self):
        await self.page.type(self.action.type_selector, self.action.type_text)

    async def handle_click(self):
        """
        Handle's clicking elements. Has additional checks to ensure that
        the element is not actually a relational hyperlink.

        This is done in the following ways:

        - We first check if the click element is actually an <a> tag
        - Or if it has a closest ancestory <a> tag

        In either case we extract the href from that <a> tag and directly goto that
        """
        click_target = self.action.click
        if click_target is None:
            return

        locator = self.page.locator(click_target)

        try:
            await locator.scroll_into_view_if_needed()
        except Exception:
            pass

        # Trying to find a hyperlink element (the target or its ancestor)
        # https://playwright.dev/python/docs/api/class-locator#locator-evaluate -> Tests a javascript expression
        try:
            href = await locator.evaluate(
                """
                el => {
                    let link = el.tagName.toLowerCase() === 'a' ? el : el.closest('a');
                    return link ? link.getAttribute('href') : null;
                }
            """
            )
        except Error:
            # Catching a strict mode violation and defaulting to the first click
            # Unfortunately playwright errors aren't fully specific
            first_locator = locator.first
            href = await first_locator.evaluate(
                """
                el => {
                    let link = el.tagName.toLowerCase() === 'a' ? el : el.closest('a');
                    return link ? link.getAttribute('href') : null;
                }
                """
            )
        if href:
            # Handling relative links by checking for a schema and a netloc (host + optional port)
            if not is_absolute_url(href):
                base_url = "/".join(self.page.url.split("/")[0:3])  # This won't be 0:3 always
                href = urljoin(base_url, href)
            await self.page.goto(href)
            await self.page.wait_for_load_state("domcontentloaded")
        else:
            try:
                await locator.click(timeout=5000)
            except Exception:
                await locator.click(force=True, timeout=5000)

    async def handle_double_click(self):
        """
        Handle's double clicking an element
        """
        await self.page.dblclick(self.action.dblclick)

    async def handle_hover(self):
        """
        Handle's hovering over an element to make new actions visible
        """
        await self.page.hover(self.action.hover)

    async def handle_checkboxes(self):
        if self.action.check:
            await self.page.check(self.action.check)
        if self.action.uncheck:
            await self.page.uncheck(self.action.uncheck)

    async def handle_select(self):
        await self.page.select_option(
            self.action.select_selector,
            value=self.action.select_value,
        )

    async def handle_file_upload(self):
        await self.page.set_input_files(
            self.action.upload_selector,
            self.action.upload_path,
        )

    # ----------------------------------
    # Handle mouse/keyboard interactions
    # ----------------------------------
    async def handle_press(self):
        """
        Handles a key press.
        """
        # If a specific selector is provided, press the key on that element.
        if self.action.press_selector and self.action.press_key:
            await self.page.press(self.action.press_selector, self.action.press_key)
        # If no selector is provided, press the key on the entire page.
        elif self.action.press_key:
            await self.page.keyboard.press(self.action.press_key)

    async def handle_keyboard_press(self):
        """
        Handles a keyboard press action on the entire page.
        """
        await self.page.keyboard.press(self.action.keyboard_press)

    async def handle_keyboard_type(self):
        await self.page.keyboard.type(self.action.keyboard_type)

    async def handle_mouse_move(self):
        await self.page.mouse.move(self.action.mouse_move_x or 0, self.action.mouse_move_y or 0)

    async def handle_mouse_click(self):
        await self.page.mouse.click(self.action.mouse_click_x or 0, self.action.mouse_click_y or 0)

    # ----------------
    # Handle scrolling
    # ----------------
    async def handle_scrolling(self):
        """
        Automates manual scrolling (or scrolls to center)
        """
        x = self.action.scroll_x or 0
        y = self.action.scroll_y or 0
        await self.page.mouse.wheel(x, y)

    # ------------
    # Handle waits
    # ------------
    async def handle_wait(self):
        if self.action.wait_selector:
            await self.page.wait_for_selector(
                self.action.wait_selector,
                timeout=self.action.wait_timeout or 5000,
            )
        elif self.action.wait_ms:
            await asyncio.sleep(self.action.wait_ms / 1000)

    # ---------------------------
    # Handle Javascript functions
    # ---------------------------
    async def handle_evaluate_js(self):
        result = await self.page.evaluate(self.action.evaluate_js)

        # Letting this be here for debugging
        print("[JS Evaluation Result]:", result)
        return result

    async def handle_screenshot(self):
        await self.page.screenshot(path=self.action.screenshot_path, full_page=True)

    async def handle_download(self):
        async with self.page.expect_download() as download_info:
            await self.page.click(self.action.download_selector)
        download = await download_info.value
        path = await download.path()
        print(f"Downloaded to: {path}")

    # -------------------
    # Handling new pages
    # -------------------
    async def handle_switch_page(self):
        context = self.page.context
        pages = context.pages
        if self.action.switch_page_index is not None and self.action.switch_page_index < len(
            pages
        ):
            self.page = pages[self.action.switch_page_index]
            await self.page.bring_to_front()

    async def handle_new_page(self):
        context = self.page.context
        new_page = await context.new_page()
        await new_page.goto(self.action.new_page)
        await new_page.wait_for_load_state("domcontentloaded")
        self.page = new_page

    async def handle_close_page(self):
        await self.page.close()

    # ----------
    # Dispatcher
    # ----------
    async def perform(self) -> None:
        """
        The main dispatch function.

        All handlers are called here as and when required by the AI models.
        Contains an exhaustive list of all the functions that can be chosen
        during the automation process
        """
        a = self.action

        if a.goto:
            return await self.handle_navigation()
        if a.go_back:
            return await self.handle_back()
        if a.go_forward:
            return await self.handle_forward()
        if a.reload:
            return await self.handle_reload()
        if a.fill_selector and a.fill_value is not None:
            return await self.handle_input()
        if a.type_selector and a.type_text:
            return await self.handle_typing()
        if a.click:
            return await self.handle_click()
        if a.dblclick:
            return await self.handle_double_click()
        if a.hover:
            return await self.handle_hover()
        if a.press_selector or a.press_key:
            return await self.handle_press()
        if a.keyboard_press:
            return await self.handle_keyboard_press()
        if a.keyboard_type:
            return await self.handle_keyboard_type()
        if a.check or a.uncheck:
            return await self.handle_checkboxes()
        if a.select_selector and a.select_value:
            return await self.handle_select()
        if a.upload_selector and a.upload_path:
            return await self.handle_file_upload()
        if a.scroll_x or a.scroll_y:
            return await self.handle_scrolling()
        if a.wait_selector or a.wait_ms:
            return await self.handle_wait()
        if a.evaluate_js:
            return await self.handle_evaluate_js()
        if a.screenshot_path:
            return await self.handle_screenshot()
        if a.download_selector:
            return await self.handle_download()
        if a.new_page:
            return await self.handle_new_page()
        if a.close_page:
            return await self.handle_close_page()
        if a.switch_page_index is not None:
            return await self.handle_switch_page()


async def perform_action(page: Page, action: PlaywrightAction) -> None:
    """
    The entry point function
    """
    # assert isinstance(action, PlaywrightAction), "the input type for action is incorrect!"
    performer = PlaywrightActionPerformer(page, action)
    await performer.perform()
