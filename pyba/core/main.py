import asyncio
import uuid
from typing import List, Union

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from pyba.core.agent.playwright_agent import PlaywrightAgent
from pyba.core.lib import HandleDependencies
from pyba.core.lib.action import perform_action
from pyba.core.lib.code_generation import CodeGeneration
from pyba.core.provider import Provider
from pyba.core.scripts import LoginEngine, ExtractionEngines
from pyba.core.tracing import Tracing
from pyba.database import Database, DatabaseFunctions
from pyba.logger import get_logger
from pyba.utils.common import initial_page_setup
from pyba.utils.exceptions import PromptNotPresent, UnknownSiteChosen, DatabaseNotInitialised
from pyba.utils.load_yaml import load_config

config = load_config("general")


class Engine:
    """
    The main entrypoint for browser automation. This engine exposes the main entry point which is the run() method
    """

    def __init__(
        self,
        openai_api_key: str = None,
        vertexai_project_id: str = None,
        vertexai_server_location: str = None,
        gemini_api_key: str = None,
        headless: bool = config["main_engine_configs"]["headless_mode"],
        handle_dependencies: bool = config["main_engine_configs"]["handle_dependencies"],
        use_logger: bool = config["main_engine_configs"]["use_logger"],
        enable_tracing: bool = config["main_engine_configs"]["enable_tracing"],
        trace_save_directory: str = None,
        database: Database = None,
    ):
        """
        Args:
            `openai_api_key`: API key for OpenAI models should you want to use that
            `vertexai_project_id`: Create a VertexAI project to use that instead of OpenAI
            `vertexai_server_location`: VertexAI server location
            `gemini_api_key`: API key for Gemini-2.5-pro native support without VertexAI
            `headless`: Choose if you want to run in the headless mode or not
            `use_logger`: Choose if you want to use the logger (that is enable logging of data)
            `handle_dependencies`: Choose if you want to automatically install dependencies during runtime
            `enable_tracing`: Choose if you want to enable tracing. This will create a .zip file which you can use in traceviewer
            `trace_save_directory`: The directory where you want the .zip file to be saved

            `database`: An instance of the Database class which will define all database specific configs

        Find these default values at `pyba/config.yaml`
        """
        self.session_id = uuid.uuid4().hex
        self.headless_mode = headless
        self.tracing = enable_tracing
        self.trace_save_directory = trace_save_directory

        # Handle database instances using `db_funcs`
        self.database = database
        self.db_funcs = DatabaseFunctions(self.database) if database else None

        # Initialising the loggering depending on whether the use_logger boolean is on
        self.log = get_logger(use_logger=use_logger)

        self.automated_login_engine_classes = []

        selectors = tuple(config["process_config"]["selectors"])
        self.combined_selector = ", ".join(selectors)

        self.handle_dependencies(handle_dependencies)

        provider_instance = Provider(
            openai_api_key=openai_api_key,
            gemini_api_key=gemini_api_key,
            vertexai_project_id=vertexai_project_id,
            vertexai_server_location=vertexai_server_location,
            logger=self.log,
        )

        self.provider = provider_instance.provider
        self.model = provider_instance.model
        self.openai_api_key = provider_instance.openai_api_key
        self.gemini_api_key = provider_instance.gemini_api_key
        self.vertexai_project_id = provider_instance.vertexai_project_id
        self.location = provider_instance.location

        # Defining the playwright agent with the defined configs
        self.playwright_agent = PlaywrightAgent(engine=self)

    @staticmethod
    def handle_dependencies(handle_dependencies: bool):
        if handle_dependencies:
            HandleDependencies.playwright.handle_dependencies()

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

        async with Stealth().use_async(async_playwright()) as p:
            self.browser = await p.chromium.launch(headless=self.headless_mode)

            tracing = Tracing(
                browser_instance=self.browser,
                session_id=self.session_id,
                enable_tracing=self.tracing,
                trace_save_directory=self.trace_save_directory,
            )
            self.trace_dir = tracing.trace_dir

            self.context = await tracing.initialize_context()
            self.page = await self.context.new_page()
            cleaned_dom = await initial_page_setup(self.page)

            for steps in range(0, config["main_engine_configs"]["max_iteration_steps"]):
                # First check if we need to login and run the scripts
                login_attempted_successfully = False

                # If loginengines have been chosen then self.automated_login_engine_classes will be populated
                if self.automated_login_engine_classes:
                    for engine in self.automated_login_engine_classes:
                        engine_instance = engine(self.page)
                        self.log.info(f"Testing for {engine_instance.engine_name} login engine")
                        # Instead of just running it and checking inside, we can have a simple lookup list
                        out_flag = await engine_instance.run()
                        if out_flag:
                            # This means it was True and we successfully logged in
                            self.log.success(
                                f"Logged in successfully through the {self.page.url} link"
                            )
                            login_attempted_successfully = True
                            break
                        elif out_flag is None:
                            # This means it wasn't for a login page for this engine
                            pass
                        else:
                            # This means it failed
                            self.log.warning(f"Login attempted at {self.page.url} but failed!")
                if login_attempted_successfully:
                    # Clean the automated_login_engine_classes
                    self.automated_login_engine_classes = None
                    # Update the DOM after a login
                    try:
                        await self.page.wait_for_load_state("networkidle", timeout=2000)
                    except Exception:
                        await asyncio.sleep(2)

                    page_html = await self.page.content()
                    body_text = await self.page.inner_text("body")
                    elements = await self.page.query_selector_all(self.combined_selector)
                    base_url = self.page.url

                    extraction_engine = ExtractionEngines(
                        html=page_html,
                        body_text=body_text,
                        elements=elements,
                        base_url=base_url,
                        page=self.page,
                    )
                    cleaned_dom = await extraction_engine.extract_all()
                    cleaned_dom.current_url = base_url

                    # Jump to the next iteration of the `for` loop
                    continue

                # Say we're going to run only 10 steps so far, so after this no more automation
                # Get an actionable PlaywrightResponse from the models
                try:
                    action = self.playwright_agent.process_action(
                        cleaned_dom=cleaned_dom.to_dict(), user_prompt=prompt
                    )
                except Exception as e:
                    self.log.error(f"something went wrong in obtaining the response: {e}")
                    action = None

                if action is None or all(value is None for value in vars(action).values()):
                    self.log.success("Automation completed, agent has returned None")
                    await self.save_trace()
                    await self.shut_down()
                    try:
                        output = self.playwright_agent.get_output(
                            cleaned_dom=cleaned_dom.to_dict(), user_prompt=prompt
                        )
                        self.log.info(f"This is the output given by the model: {output}")
                        return output
                    except Exception:
                        # Usually a resource exhausted error
                        await asyncio.sleep(10)
                        output = self.playwright_agent.get_output(
                            cleaned_dom=cleaned_dom.to_dict(), user_prompt=prompt
                        )
                        self.log.info(f"This is the output given by the model: {output}")
                        return output

                self.log.action(action)
                if self.db_funcs:
                    self.db_funcs.push_to_episodic_memory(
                        session_id=self.session_id, action=str(action), page_url=str(self.page.url)
                    )
                # If its not None, then perform it
                await perform_action(self.page, action)

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

        await self.save_trace()
        await self.shut_down()

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

    def sync_run(
        self, prompt: str = None, automated_login_sites: List[str] = None
    ) -> Union[str, None]:
        """
        Sync endpoint for running the above function
        """
        output = asyncio.run(self.run(prompt=prompt, automated_login_sites=automated_login_sites))

        if output:
            return output

    def generate_code(self, output_path: str) -> bool:
        """
        Function end-point for code generation

        Args:
            `output_path`: output file path to save the generated code to
        """
        if not self.db_funcs:
            raise DatabaseNotInitialised()

        codegen = CodeGeneration(
            session_id=self.session_id, output_path=output_path, database_funcs=self.db_funcs
        )
        codegen.generate_script()
        self.log.info(f"Created the script at: {output_path}")
        return True
