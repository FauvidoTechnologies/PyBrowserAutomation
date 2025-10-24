import os
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
from playwright.async_api import Page

from pyba.utils.exceptions import CredentialsnotSpecified
from pyba.utils.load_yaml import load_config

load_dotenv()  # Loading the username and passwords
config = load_config()["automated_login_configs"]["facebook"]


class FacebookLogin:
    """
    The instagram login engine
    """

    def __init__(self, page: Page) -> None:
        self.page = (
            page  # This is the page we're at, this is where the login automation needs to happen
        )

        self.engine_name = "instagram"
        self.username = os.getenv("facebook_username")
        self.password = os.getenv("facebook_password")

        if self.username is None or self.password is None:
            raise CredentialsnotSpecified(self.engine_name)

        self.uses_2FA = False

    def verify_login_page(self):
        """
        Make sure that the script we're going to run is made for this login page itself. This uses multiple ways to
        ensure that. First it verifies it through the URL, then checks if the elements we are going to append to.
        """

        page_url = self.page.url

        facebook_urls = list(config["urls"])

        # We'll have to clean the URL from all the url formatting to the basic thing and match it with this.
        # This can be done using urlparse and normalizing it first
        parsed = urlparse(page_url)
        normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        if not normalized_url.endswith("/"):
            normalized_url += "/"

        # Keeping it simple with this right now, later we can make this better
        if normalized_url in facebook_urls:
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
            await self.page.wait_for_selector('input[name="email"]')
            await self.page.fill('input[name="email"]', self.username)
            await self.page.fill('input[name="pass"]', self.password)

            await self.page.click('button[type="submit"]')
        except Exception:
            # Now this is bad
            return False

        try:
            await self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            # It's fine, we'll assume that the login worked nicely
            pass

        return True
