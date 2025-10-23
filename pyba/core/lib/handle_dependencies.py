import os
import re
import subprocess
import sys


class PlaywrightDependencies:
    """
    We'll make use of this class if the user wants us to handle the dependencies. Usually, this
    shouldn't be the case because its like 2 commands to manage all playwright deps.
    """

    @staticmethod
    def check_playwright_browsers_installed() -> bool:
        """
        Checking if playwright browsers are installed by pipeing the output of a dry-run
        and verifying certain regex matches along with checking the cache directory where
        we expect the browsers to be.
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "--dry-run"],
                capture_output=True,
                text=True,
                check=False,
            )

            stdout = result.stdout.lower()

            # Looking for `downloading` text
            if re.search(r"install location:", stdout) and not re.search(
                r"(installing|downloading)", stdout
            ):
                return True

            # We can just check the cache directory as well (hopefully this is not a violation of anything...)
            cache_dir = os.path.expanduser("~/.cache/ms-playwright")
            expected_dirs = [
                "chromium-",
                "chromium_headless_shell-",
                "firefox-",
                "webkit-",
                "ffmpeg-",
            ]

            # Checking if each expected browser has at least one matching folder
            installed = (
                all(
                    any(name.startswith(prefix) for name in os.listdir(cache_dir))
                    for prefix in expected_dirs
                )
                if os.path.exists(cache_dir)
                else False
            )

            return installed

        except Exception:
            return False

    @staticmethod
    def install_playwright_browsers():
        """
        Install Playwright browsers automatically.
        """
        print("Installing Playwright browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)

    @staticmethod
    def check_missing_dependencies():
        """
        Run a test to identify missing dependencies using `playwright install-deps --dry-run`.
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install-deps", "--dry-run"],
                capture_output=True,
                text=True,
                check=False,
            )
            output = result.stdout.strip() + "\n" + result.stderr.strip()
            # Filter only the lines that mention missing libraries
            missing_lines = [
                line
                for line in output.splitlines()
                if "Missing" in line or line.strip().endswith(".so") or "║" in line
            ]
            if missing_lines:
                print("The following dependencies are missing: ")
                print("\n".join(missing_lines))
                print(
                    "Please install them manually using your package manager or run: playwright install-deps"
                )

            else:
                print("All playwright dependencies present")
        except FileNotFoundError:
            print("Could not run playwright. Is it installed in this environment?")

    @staticmethod
    def handle_dependencies():
        # Step 1: Check if browsers are installed
        if PlaywrightDependencies.check_playwright_browsers_installed():
            print("Playwright browsers are already installed")
        else:
            print("Playwright browsers not found.")
            choice = input("Do you want to install them automatically? (y/n): ").strip().lower()
            if choice == "y":
                PlaywrightDependencies.install_playwright_browsers()
            else:
                print("Please install browsers using: playwright install")
        # Step 2: Check missing system dependencies
        PlaywrightDependencies.check_missing_dependencies()


class HandleDependencies:
    playwright = PlaywrightDependencies
