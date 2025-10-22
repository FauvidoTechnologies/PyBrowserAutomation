import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from playwright.async_api import Page

load_dotenv()  # Loading the username and passwords

SCREEN_HEIGHT = 1280  # my screen's height, we need this to be in the config as well!
x_from_left = 1000
y_from_bottom = 1000
y_top_left = SCREEN_HEIGHT - y_from_bottom


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

        self.uses_2FA = False

    def verify_login_page(self):
        """
        Make sure that the script we're going to run is made for this login page itself. This uses multiple ways to
        ensure that. First it verifies it through the URL, then checks if the elements we are going to append to.
        """

        page_url = self.page.url

        # This needs to be taken from a config file. I will start maintaing that later
        instagram_urls = [
            "https://www.instagram.com/accounts/login/",
            "https://www.instagram.com/",
        ]

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

    def run(self) -> None:
        """
        The idea is to take in the username and password from the .env file for now
        and simply use that to execute this function

        Returns:
                `None` if we're not supposed to launch the automated login script here
        """
        val = self.verify_login_page()
        if not val:
            return None

        # Now run the script
        self.page.wait_for_selector('input[name="username"]')
        self.page.fill('input[name="username"]', self.username)
        self.page.fill('input[name="password"]', self.password)

        self.page.click('button[type="submit"]')

        # There is a not-now button that we need to click for not saving our information
        try:
            self.page.wait_for_selector('text="Not now"', timeout=30000)
            self.page.click('text="Not now"')
        except Exception:
            # This means that never came so we're done.
            pass

        # Sometimes these things also come up for new updates
        try:
            self.page.wait_for_selector('text="OK"', timeout=10000)
            self.page.mouse.click(x_from_left, y_top_left)
        except Exception:
            # This means this never came up
            pass

        self.page.wait_for_load_state("networkidle")
