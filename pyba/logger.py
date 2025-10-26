from typing import Optional

import colorama
from colorama import Fore, Style

# Initialize colorama to auto-reset styles after each print
colorama.init(autoreset=True)


class Logger:
    """
    Custom logger for PyBA. This only logs if 'use_logger' is enabled.
    """

    def __init__(self, use_logger: bool = False):
        """
        Args:
            use_logger (bool): If False, all logging methods will do nothing.
        """
        self.use_logger = use_logger
        if self.use_logger:
            self.info("Logger initialized. Logging is enabled.")

    def _log(self, prefix: str, message: str, color: str):
        if not self.use_logger:
            return
        print(f"{Style.BRIGHT}{color}{prefix}{Style.NORMAL}{Fore.RESET} {message}")

    def info(self, message: str):
        self._log("[INFO]   ", message, Fore.BLUE)

    def success(self, message: str):
        self._log("[SUCCESS]", message, Fore.GREEN)

    def warning(self, message: str):
        self._log("[WARNING]", message, Fore.YELLOW)

    def error(self, message: str, e: Optional[Exception] = None):
        if e:
            message = f"{message}: {e}"
        self._log("[ERROR]  ", message, Fore.RED)

    def action(self, message: str):
        self._log("[ACTION] ", message, Fore.MAGENTA)


def get_logger(use_logger: bool = False) -> Logger:
    """
    Factory function to get a Logger instance.

    Args:
        use_logger (bool): Flag to enable or disable logging.

    Returns:
        Logger: An instance of the Logger class.
    """
    return Logger(use_logger=use_logger)
