import asyncio

from pyba.core.scripts import ExtractionEngines
from pyba.database import DatabaseFunctions
from pyba.logger import setup_logger, get_logger


class BaseEngine:
    """
    A reusable base class that encapsulates the shared browser lifecycle,
    tracing, DOM extraction, and utility helpers.

        The following will be initialised by the BaseEngine:

        - `db_funcs`: The database functions to be used for inserting and querying logs
    """

    def __init__(
        self,
        headless=True,
        enable_tracing=True,
        trace_save_directory=None,
        database=None,
        use_logger=None,
    ):
        self.headless_mode = headless
        self.tracing = enable_tracing
        self.trace_save_directory = trace_save_directory

        self.database = database
        self.db_funcs = DatabaseFunctions(self.database) if database else None

        setup_logger(use_logger=use_logger)
        self.log = get_logger()

    async def extract_dom(self):
        """
        Extracts the relevant fields from the DOM of the current page and returns
        the DOM dataclass.
        """
        try:
            await self.page.wait_for_load_state(
                "networkidle", timeout=1000
            )  # Wait for a second for network calls to stablize
            page_html = await self.page.content()
        except Exception:
            # We might get a "Unable to retrieve content because the page is navigating and changing the content" exception
            # This might happen because page.content() will start and issue an evaluate, while the page is reloading and making network calls
            # So, once it gets a response, it commits it and clears the execution contents so page.content() fails.
            # See https://github.com/microsoft/playwright/issues/16108

            # We might choose to wait for networkidle -> https://github.com/microsoft/playwright/issues/22897
            try:
                await self.page.wait_for_load_state("networkidle", timeout=2000)
            except Exception:
                # If networkidle never happens, then we'll try a direct wait
                await asyncio.sleep(3)

            page_html = await self.page.content()

        body_text = await self.page.inner_text("body")
        elements = await self.page.query_selector_all(self.combined_selector)
        base_url = self.page.url

        # Then we need to extract the new cleaned_dom from the page
        # Passing in known_fields for the input fields that we already know off so that
        # its easier for the extraction engine to work
        extraction_engine = ExtractionEngines(
            html=page_html,
            body_text=body_text,
            elements=elements,
            base_url=base_url,
            page=self.page,
        )

        # Perform an all out extraction
        cleaned_dom = await extraction_engine.extract_all()
        cleaned_dom.current_url = base_url
        return cleaned_dom

    async def generate_output(self, action, cleaned_dom, prompt):
        """
        Helper function to generate the output if the action
        has been completed.

        Args:
            `action`: The action as given out by the model
            `cleaned_dom`: The latest cleaned_dom for the model to read
            `prompt`: The prompt which was given to the model
        """
        if action is None or all(value is None for value in vars(action).values()):
            self.log.success("Automation completed, agent has returned None")
            try:
                output = self.playwright_agent.get_output(
                    cleaned_dom=cleaned_dom.to_dict(), user_prompt=prompt
                )
                self.log.info(f"This is the output given by the model: {output}")
                return output
            except Exception:
                # This should rarely happen
                await asyncio.sleep(10)
                output = self.playwright_agent.get_output(
                    cleaned_dom=cleaned_dom.to_dict(), user_prompt=prompt
                )
                self.log.info(f"This is the output given by the model: {output}")
                return output
        else:
            return None

    async def save_trace(self):
        """
        Endpoint to save the trace if required
        """
        if self.tracing:
            trace_path = self.trace_dir / f"{self.session_id}_trace.zip"
            self.log.info(f"This is the tracepath: {trace_path}")
            await self.context.tracing.stop(path=str(trace_path))

    async def shut_down(self):
        """
        Function to cleanly close the existing browsers and contexts. This also saves
        the traces in the provided trace_dir by the user or the default.
        """
        await self.context.close()
        await self.browser.close()
