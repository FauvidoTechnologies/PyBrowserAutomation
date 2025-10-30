from pathlib import Path

from pyba.utils.load_yaml import load_config

config = load_config("general")["main_engine_configs"]


class Tracing:
    """
    Class to manage all tracing functions
    """

    def __init__(
        self,
        browser_instance,
        session_id: str,
        enable_tracing: bool = False,
        trace_save_directory: str = None,
    ):
        """
        Args:
                `browser_instance`: The browser instance being used under the main async with statement
                `session_id`: A unique identifier for this session
                `enable_tracing`: A boolean to indicate the use of tracing
                `trace_save_directory`: Directory to save the traces

        """
        self.browser = browser_instance

        self.session_id = session_id
        self.enable_tracing = enable_tracing
        self.trace_save_directory = trace_save_directory

    async def initialize_context(self):
        if self.enable_tracing:
            if self.trace_save_directory is None:
                # This means we revert to default
                trace_save_directory = config["trace_save_directory"]
            else:
                trace_save_directory = self.trace_save_directory

            self.trace_dir = Path(trace_save_directory)
            self.trace_dir.mkdir(parents=True, exist_ok=True)
            har_file_path = self.trace_dir / f"{self.session_id}_network.har"

            context = await self.browser.new_context(
                record_har_path=har_file_path,  # HAR file output
                record_har_content=config["tracing"][
                    "record_har_content"
                ],  # include request/response bodies
            )
        else:
            context = await self.browser.new_context()

        return context
