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
        screenshots: bool = False,
        snapshots: bool = False,
        sources: bool = False,
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

        self.screenshots: bool = config["tracing"]["screenshots"] | screenshots
        self.snapshots: bool = config["tracing"]["snapshots"] | snapshots
        self.sources: bool = config["tracing"]["sources"] | sources

        if self.trace_save_directory is None:
            # This means we revert to default, which is CWD
            trace_save_directory = str(Path.cwd())
        else:
            trace_save_directory = self.trace_save_directory

        self.trace_dir = Path(trace_save_directory)
        self.trace_dir.mkdir(parents=True, exist_ok=True)

        self.har_file_path = self.trace_dir / f"{self.session_id}_network.har"

    async def initialize_context(self):
        if self.enable_tracing:
            context = await self.browser.new_context(
                record_har_path=self.har_file_path,  # HAR file output
                record_har_content=config["tracing"][
                    "record_har_content"
                ],  # include request/response bodies
                viewport={
                    "width": 1920,
                    "height": 1080,
                },  # Including a generic viewport, can later move this to config
            )

            await context.tracing.start(
                screenshots=self.screenshots,
                snapshots=self.snapshots,
                sources=self.sources,
            )

        else:
            context = await self.browser.new_context(viewport={"width": 1920, "height": 1080})

        return context
