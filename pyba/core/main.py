import asyncio
import sys
import uuid
from pathlib import Path
from typing import List

from playwright.async_api import async_playwright

from pyba.core.agent.playwright_agent import PlaywrightAgent
from pyba.core.lib import DOMExtraction, HandleDependencies
from pyba.core.lib.action import perform_action
from pyba.core.scripts import LoginEngine
from pyba.utils.exceptions import (
    PromptNotPresent,
    ServiceNotSelected,
    ServerLocationUndefined,
    UnknownSiteChosen,
)
from pyba.utils.load_yaml import load_config

config = load_config()


class Engine:
    """
    The main entrypoint for browser automation. This engine exposes the main entry point which is the run() method
    """

    def __init__(
        self,
        openai_api_key: str = None,
        vertexai_project_id: str = None,
        vertexai_server_location: str = None,
        headless: bool = config["main_engine_configs"]["headless_mode"],
        handle_dependencies: bool = config["main_engine_configs"]["handle_dependencies"],
        enable_tracing: bool = config["main_engine_configs"]["enable_tracing"],
        trace_save_directory: str = None,
    ):
        """
        Args:
            openai_api_key: API key for OpenAI models should you want to use that
            vertexai_project_id: Create a VertexAI project to use that instead of OpenAI
            vertexai_server_location: VertexAI server location
            headless: Choose if you want to run in the headless mode or not
            handle_dependencies: Choose if you want to automatically install dependencies during runtime
            enable_tracing: Choose if you want to enable tracing. This will create a .zip file which you can use in traceviewer
            trace_save_directory: The directory where you want the .zip file to be saved

        Find these default values at `pyba/config.yaml`
        """
        self.provider = None
        self.session_id = uuid.uuid4().hex
        self.headless_mode = headless
        self.tracing = enable_tracing
        self.trace_save_directory = trace_save_directory

        self.automated_login_engine_classes = []

        selectors = tuple(config["process_config"]["selectors"])
        self.combined_selector = ", ".join(selectors)

        self.handle_dependencies(handle_dependencies)
        self.handle_keys(openai_api_key, vertexai_project_id, vertexai_server_location)
        # Defining the playwright agent with the defined configs
        self.playwright_agent = PlaywrightAgent(engine=self)  # This is amusing

    def handle_dependencies(self, handle_dependencies: bool):
        if handle_dependencies:
            HandleDependencies.playwright.handle_dependencies()

    def handle_keys(self, openai_api_key, vertexai_project_id, vertexai_server_location):
        if openai_api_key is None and vertexai_project_id is None:
            raise ServiceNotSelected()

        if vertexai_project_id and vertexai_server_location is None:
            raise ServerLocationUndefined(vertexai_server_location)

        if openai_api_key and vertexai_project_id:
            print(
                "You've defined both vertexai and openai models, we're choosing to go with openai!"
            )
            self.openai_api_key = openai_api_key
            self.provider = config["main_engine_configs"]["openai"]["provider"]

        if vertexai_project_id:
            # Assuming that we don't have an openai_api_key
            self.provider = config["main_engine_configs"]["vertexai"]["provider"]
            self.vertexai_project_id = vertexai_project_id
            self.location = vertexai_server_location
            self.model = config["main_engine_configs"]["vertexai"]["model"]
        else:
            self.provider = config["main_engine_configs"]["openai"]["provider"]
            self.openai_api_key = openai_api_key

    async def run(self, prompt: str = None, automated_login_sites: List[str] = None):
        """
        The most basic implementation for the run function

        Args:
            `prompt`: The user's instructions
                Right now we're assuming that the user's prompt is well defined. In later
                versions we'll come up with a fix for that as well.
        """

        if prompt is None:
            raise PromptNotPresent()

        if automated_login_sites is not None:
            assert isinstance(
                automated_login_sites, list
            ), "Make sure the automated_login_sites is a list!"

            for engine in automated_login_sites:
                # Each engine is going to be a name like "instagram"
                if hasattr(LoginEngine, engine):
                    engine_class = getattr(LoginEngine, engine)
                    self.automated_login_engine_classes.append(engine_class)
                else:
                    raise UnknownSiteChosen(LoginEngine.available_engines())

        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=False)

            # Start tracing if enabled
            if self.tracing:
                # First create the directory for saving
                if self.trace_save_directory is None:
                    # This means we revert to default
                    trace_save_directory = config["main_engine_configs"]["trace_save_directory"]
                else:
                    trace_save_directory = self.trace_save_directory

                self.trace_dir = Path(trace_save_directory)
                self.trace_dir.mkdir(parents=True, exist_ok=True)
                har_file_path = self.trace_dir / f"{self.session_id}_network.har"

                self.context = await self.browser.new_context(
                    record_har_path=har_file_path,  # HAR file output
                    record_har_content=config["main_engine_configs"]["tracing"][
                        "record_har_content"
                    ],  # include request/response bodies
                )

                await self.context.tracing.start(
                    # By default, all of them are False
                    screenshots=config["main_engine_configs"]["tracing"]["screenshots"],
                    snapshots=config["main_engine_configs"]["tracing"]["snapshots"],
                    sources=config["main_engine_configs"]["tracing"]["sources"],
                )
            else:
                # Normal context without tracing enabled
                self.context = await self.browser.new_context()

            self.page = await self.context.new_page()

            cleaned_dom = {
                "hyperlinks": None,
                "input_fields": None,
                "clickable_fields": None,
                "actual_text": None,
                "current_url": None,
            }

            for steps in range(0, config["main_engine_configs"]["max_iteration_steps"]):
                # First check if we need to login and run the scripts
                # If loginengines have been chosen then self.automated_login_engine_classes will be populated
                if self.automated_login_engine_classes:
                    for engine in self.automated_login_engine_classes:
                        engine_instance = engine(self.page)
                        # Instead of just running it and checking inside, we can have a simple lookup list
                        out_flag = await engine_instance.run()
                        if out_flag:
                            # This means it was True and we successfully logged in
                            print(f"Logged in successfully through the {self.page.url} link")
                        elif out_flag is None:
                            # This means it wasn't for a login page for this engine
                            pass
                        else:
                            # This means it failed
                            print(f"Login attempted at {self.page.url} but failed!")

                # Say we're going to run only 10 steps so far, so after this no more automation
                # Get an actionable PlaywrightResponse from the models
                try:
                    action = self.playwright_agent.process_action(
                        cleaned_dom=cleaned_dom, user_prompt=prompt
                    )
                except Exception as e:
                    print(f"something went wrong in obtaining the response: {e}")
                    action = None

                if action is None or all(value is None for value in vars(action).values()):
                    print("Automation completed, agent has returned None")
                    await self.shut_down()

                # If its not None, then perform it
                await perform_action(self.page, action)

                page_html = await self.page.content()
                body_text = await self.page.inner_text("body")
                elements = await self.page.query_selector_all(self.combined_selector)
                base_url = self.page.url

                # Then we need to extract the new cleaned_dom from the page
                extractionEngine = DOMExtraction(
                    html=page_html, body_text=body_text, elements=elements, base_url=base_url
                )

                # Passing in known_fields for the input fields that we already know off so that
                # its easier for the extraction engine to work
                cleaned_dom = await extractionEngine.extract()

                cleaned_dom["current_url"] = base_url

        await self.shut_down()

    async def shut_down(self):
        """
        Function to cleanly close the existing browsers and contexts. This also saves
        the traces in the provided trace_dir by the user or the default.
        """
        if self.tracing:
            trace_path = self.trace_dir / f"{self.session_id}_trace.zip"
            print(f"This is the tracepath: {trace_path}")
            await self.context.tracing.stop(path=str(trace_path))

        await self.context.close()
        await self.browser.close()
        sys.exit(0)

    def sync_run(self, prompt: str = None, automated_login_sites: List[str] = None):
        """
        Sync endpoint for running the above function
        """
        asyncio.run(self.run(prompt=prompt, automated_login_sites=automated_login_sites))
