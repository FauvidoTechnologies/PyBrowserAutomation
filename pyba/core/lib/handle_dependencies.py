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
        Check if Playwright browsers are installed by running `playwright install --dry-run`
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "--dry-run"],
                capture_output=True,
                text=True,
                check=False,
            )
            # If dry-run shows no browsers to install, they are already installed
            return "No browsers to install" in result.stdout
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
                print("Please install them manually using your package manager or run: playwright install-deps")

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
