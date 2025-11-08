from playwright.async_api import Page

from pyba.core.scripts.login.base import BaseLogin


class FacebookLogin(BaseLogin):
    """
    The facebook login engine, inherited form the BaseLogin class
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page, engine_name="facebook")

    async def _perform_login(self) -> bool:
        try:
            await self.page.wait_for_selector(self.config["username_selector"])
            await self.page.fill(self.config["username_selector"], self.username)
            await self.page.fill(self.config["password_selector"], self.password)
            await self.page.click(self.config["submit_selector"])
        except Exception:
            # Now this is bad
            return False

        return True
