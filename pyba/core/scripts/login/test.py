from playwright.sync_api import sync_playwright

SCREEN_HEIGHT = 1280  # your screen/viewport height
x_from_left = 1000
y_from_bottom = 1000

# Convert bottom-left origin → top-left (Playwright's system)
y_top_left = SCREEN_HEIGHT - y_from_bottom


def login_instagram(username: str, password: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # set to True if you don't want the UI
        page = browser.new_page()

        # Go to Instagram login page
        page.goto("https://www.instagram.com/accounts/login/")

        # Wait for the login form to appear
        page.wait_for_selector('input[name="username"]')

        # Fill in username and password
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)

        # Click the login button
        page.click('button[type="submit"]')

        page.wait_for_selector('text="Not now"', timeout=30000)
        page.click('text="Not now"')

        # This is a seasonal thing, we might not always need this but its fine for now
        page.wait_for_selector('text="OK"', timeout=10000)
        page.mouse.click(x_from_left, y_top_left)

        # Wait for navigation to home or for an error
        page.wait_for_load_state("networkidle")

        # (Optional) verify successful login
        if "accounts/onetap" in page.url or "challenge" in page.url:
            print("Login may require verification.")
        elif "instagram.com" in page.url:
            print("Login successful!")
        else:
            print("Login failed!")

        browser.close()


if __name__ == "__main__":
    login_instagram("axchintyx", "purge_1i9i")
