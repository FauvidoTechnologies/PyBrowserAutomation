from playwright.async_api import Page

from pyba.utils.structure import PlaywrightAction


class PlaywrightActionPerformer:
    """
    The playwright automation class. To add new handles, make a function here
    and define that under perform()
    """

    def __init__(self, page: Page, action: PlaywrightAction):
        self.page = page
        self.action = action

    async def handle_navigation(self):
        """
        Handle's browser naviation -> Opening new websites
        Wait's until the page is loaded
        """
        await self.page.goto(self.action.goto)
        await self.page.wait_for_load_state("domcontentloaded")

    async def handle_input(self):
        """
        Inputs a value to a selector field
        """
        await self.page.fill(self.action.fill_selector, self.action.fill_value)

    async def handle_click(self):
        """
        Handle's clicking elements. Has additional checks to ensure that
        the element is not actually a relational hyperlink
        """
        click_target = self.action.click

        # Handle relational hyperlinks seperately
        if click_target.startswith("a[href=") or "href=" in click_target:
            href = click_target.split('"')[1]
            if href.startswith("/"):
                base_url = self.page.url.split("/")[0:3]
                href = "/".join(base_url) + href
            await self.page.goto(href)
            await self.page.wait_for_load_state("domcontentloaded")
        else:
            locator = self.page.locator(click_target)
            try:
                await locator.scroll_into_view_if_needed()
                await locator.click(timeout=5000)
            except Exception:
                # Try to force a click
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

    async def handle_checkboxes(self):
        """
        Checking and unchecking of boxes
        """
        if self.action.check:
            await self.page.check(self.action.check)
        if self.action.uncheck:
            await self.page.uncheck(self.action.uncheck)

    async def handle_scrolling(self):
        """
        Automates manual scrolling (or scrolls to center)
        """
        x = self.action.scroll_x or 0
        y = self.action.scroll_y or 0
        await self.page.mouse.wheel(x, y)

    async def perform(self) -> None:
        """
        This is the main dispatch function. All handlers are called here
        as and when required by the AI models.
        """
        action = self.action

        if action.goto:
            await self.handle_navigation()
            return

        if action.fill_selector and action.fill_value is not None:
            await self.handle_input()
            return

        if action.click:
            await self.handle_click()
            return

        if action.dblclick:
            await self.handle_double_click()
            return

        if action.hover:
            await self.handle_hover()
            return

        # Handle the specific case of press_selector and press_key together
        if action.press_selector and action.press_key:
            await self.handle_press()
            return

        # Handle the specific case of keyboard_press on its own
        if action.keyboard_press:
            await self.handle_keyboard_press()
            return

        if action.check or action.uncheck:
            await self.handle_checkboxes()
            return

        if action.scroll_x or action.scroll_y:
            await self.handle_scrolling()
            return


async def perform_action(page: Page, action: PlaywrightAction) -> None:
    """
    The entry point function
    """
    # assert isinstance(action, PlaywrightAction), "the input type for action is incorrect!"
    performer = PlaywrightActionPerformer(page, action)
    await performer.perform()
