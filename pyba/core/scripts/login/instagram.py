import os
from typing import Optional

from dotenv import load_dotenv
from playwright.async_api import Page

from pyba.utils.common import verify_login_page
from pyba.utils.exceptions import CredentialsnotSpecified
from pyba.utils.load_yaml import load_config

load_dotenv()  # Loading the username and passwords
config = load_config("general")["automated_login_configs"]["instagram"]

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

    async def run(self) -> Optional[bool]:
        """
        The idea is to take in the username and password from the .env file for now
        and simply use that to execute this function

        Returns:
                `None` if we're not supposed to launch the automated login script here
                `True/False` if the login was successful or a failure
        """
        val = verify_login_page(page_url=self.page.url, url_list=list(config["urls"]))

        if not val:
            return None

        # Now run the script
        try:
            await self.page.wait_for_selector(config["username_selector"])
            await self.page.fill(config["username_selector"], self.username)
            await self.page.fill(config["password_selector"], self.password)

            await self.page.click(config["submit_selector"])
        except Exception:
            try:
                # Alternate fields that instagram uses
                await self.page.wait_for_selector(config["fallback"]["username_selector"])
                await self.page.fill(config["fallback"]["username_selector"], self.username)
                await self.page.fill(config["fallback"]["password_selector"], self.password)

                await self.page.click(config["submit_selector"])
            except Exception:
                return False
        # There is a not-now button that we need to click for not saving our information
        try:
            await self.page.wait_for_selector(
                config["additional_args"]["additional_selector_1"], timeout=30000
            )
            await self.page.click(config["additional_args"]["additional_selector_1"])
        except Exception:
            # This means that never came so we're done.
            pass

        # Sometimes these things also come up for new updates
        try:
            await self.page.wait_for_selector(
                config["additional_args"]["additional_selector_2"], timeout=10000
            )
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
