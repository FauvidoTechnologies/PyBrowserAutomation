import os
import re
from typing import Optional

from dotenv import load_dotenv
from playwright.async_api import Page

from pyba.utils.common import verify_login_page
from pyba.utils.exceptions import CredentialsnotSpecified
from pyba.utils.load_yaml import load_config

load_dotenv()  # Loading the username and passwords
config = load_config("general")["automated_login_configs"]["gmail"]


class GmailLogin:
    """
    The instagram login engine
    """

    def __init__(self, page: Page) -> None:
        self.page = (
            page  # This is the page we're at, this is where the login automation needs to happen
        )

        self.engine_name = "gmail"
        self.username = os.getenv("gmail_username")
        self.password = os.getenv("gmail_password")

        if self.username is None or self.password is None:
            raise CredentialsnotSpecified(self.engine_name)

        self.uses_2FA = config["uses_2FA"]
        self.final_2FA_url = re.compile(config["2FA_wait_value"])

    async def run(self) -> Optional[bool]:
        """
        Take in the username and password from the .env file and use
        them to execute this function

        Returns:
                `None` if we're not supposed to launch the automated login script here
                `True/False` if the login was successful or a failure

        The return type triggers the main execution loop of the login status
        """
        val = verify_login_page(page_url=self.page.url, url_list=list(config["urls"]))
        if not val:
            return None

        # Run the script
        try:
            await self.page.wait_for_selector(config["username_selector"])
            await self.page.fill(config["username_selector"], self.username)

            await self.page.click(
                config["submit_selector"]
            )  # It's usually a next button in gmail/accounts.google.com
        except Exception:
            # Google's too smart
            return False

        try:
            # TODO: Move this to config and take type=password as well into consideration
            await self.page.wait_for_selector(config["password_selector"])
            await self.page.fill(config["password_selector"], self.password)

            await self.page.click(config["submit_selector"])
        except Exception:
            # Now this is bad
            try:
                # Alternate fields that gmail might use uses
                await self.page.wait_for_selector(config["fall_back"]["password_selector"])
                await self.page.fill(config["fall_back"]["password_selector"], self.password)

                await self.page.click(config["submit_selector"])
            except Exception:
                return False

        try:
            await self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            # It's fine, we'll assume that the login worked nicely
            pass

        if self.uses_2FA:
            # In this case, wait for the user to authenticate manually before resuming automation again
            await self.page.wait_for_url(
                self.final_2FA_url
            )  # Waiting for the page to contain 'mail.google.com'

        return True
