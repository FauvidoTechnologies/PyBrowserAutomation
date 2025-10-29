import os
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
from playwright.async_api import Page

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

        self.uses_2FA = True

    def verify_login_page(self):
        """
        Make sure that the script we're going to run is made for this login page itself. This uses multiple ways to
        ensure that. First it verifies it through the URL, then checks if the elements we are going to append to.
        """

        page_url = self.page.url

        print(f"this is the page_url: {page_url}")

        gmail_urls = list(config["urls"])
        print(gmail_urls)

        # We'll have to clean the URL from all the url formatting to the basic thing and match it with this.
        # This can be done using urlparse and normalizing it first
        parsed = urlparse(page_url)
        print(f"parsed page url: {parsed}")
        normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        print(f"normalized_url: {normalized_url}")

        if not normalized_url.endswith("/"):
            normalized_url += "/"

        # Keeping it simple with this right now, later we can make this better
        if normalized_url in gmail_urls:
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
            await self.page.wait_for_selector('input[name="identifier"]')
            await self.page.fill('input[name="identifier"]', self.username)

            await self.page.click(
                'text="Next"'
            )  # It's usually a next button in gmail/accounts.google.com
        except Exception:
            # Google's too smart
            return False

        try:
            # TODO: Move this to config and take type=password as well into consideration
            await self.page.wait_for_selector('input[name="Passwd"]')
            await self.page.fill('input[name="Passwd"]', self.password)

            await self.page.click('text="Next"')
        except Exception:
            # Now this is bad
            try:
                # Alternate fields that gmail might use uses
                await self.page.wait_for_selector('input[name="password"]')
                await self.page.fill('input[name="password"]', self.password)

                await self.page.click('text="Next"')
            except Exception:
                return False

        try:
            await self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            # It's fine, we'll assume that the login worked nicely
            pass

        return True
