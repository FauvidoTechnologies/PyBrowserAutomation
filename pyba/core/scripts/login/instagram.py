import os
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
from playwright.async_api import Page

from pyba.utils.exceptions import CredentialsnotSpecified
from pyba.utils.load_yaml import load_config

load_dotenv()  # Loading the username and passwords
config = load_config()["automated_login_configs"]["instagram"]

screen_height = config["click_location"]["default_screen_height"]
x_from_left = config["click_location"]["x_from_left"]
y_from_bottom = config["click_location"]["y_from_bottom"]
y_top_left = screen_height - y_from_bottom


class InstagramLogin:
    """
    The instagram login engine
    """

    def __init__(self, page: Page) -> None:
        self.page = (
            page  # This is the page we're at, this is where the login automation needs to happen
        )

        self.engine_name = "instagram"
        self.username = os.getenv("instagram_username")
        self.password = os.getenv("instagram_password")

        if self.username is None or self.password is None:
            raise CredentialsnotSpecified(self.engine_name)

        self.uses_2FA = False

    def verify_login_page(self):
        """
        Make sure that the script we're going to run is made for this login page itself. This uses multiple ways to
        ensure that. First it verifies it through the URL, then checks if the elements we are going to append to.
        """

        page_url = self.page.url

        instagram_urls = list(config["urls"])

        # We'll have to clean the URL from all the url formatting to the basic thing and match it with this.
        # This can be done using urlparse and normalizing it first
        parsed = urlparse(page_url)
        normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        if not normalized_url.endswith("/"):
            normalized_url += "/"

        # Keeping it simple with this right now, later we can make this better
        if normalized_url in instagram_urls:
            return True
        else:
            return False

    async def run(self) -> Optional[bool]:
        """
        The idea is to take in the username and password from the .env file for now
        and simply use that to execute this function

        Returns:
                `None` if we're not supposed to launch the automated login script here
                `True/False` if the login was successful or a failure
        """
        val = self.verify_login_page()
        if not val:
            return None

        # Now run the script
        try:
            await self.page.wait_for_selector('input[name="username"]')
            await self.page.fill('input[name="username"]', self.username)
            await self.page.fill('input[name="password"]', self.password)

            await self.page.click('button[type="submit"]')
        except Exception:
            # Now this is bad
            try:
                # Alternate fields that instagram uses
                await self.page.wait_for_selector('input[name="email"]')
                await self.page.fill('input[name="email"]', self.username)
                await self.page.fill('input[name="pass"]', self.password)

                await self.page.click('button[type="submit"]')
            except Exception:
                return False
        # There is a not-now button that we need to click for not saving our information
        try:
            await self.page.wait_for_selector('text="Not now"', timeout=30000)
            await self.page.click('text="Not now"')
        except Exception:
            # This means that never came so we're done.
            pass

        # Sometimes these things also come up for new updates
        try:
            await self.page.wait_for_selector('text="OK"', timeout=10000)
            await self.page.mouse.click(x_from_left, y_top_left)
        except Exception:
            # This means this never came up
            pass

        try:
            await self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            # It's fine, we'll assume that the login worked nicely
            pass

        return True
