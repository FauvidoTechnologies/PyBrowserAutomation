import asyncio
import uuid
from typing import List, Union

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from pyba.core.lib.action import perform_action
from pyba.core.lib.mode.base import BaseEngine
from pyba.core.scripts import LoginEngine
from pyba.database import Database
from pyba.utils.common import initial_page_setup
from pyba.utils.exceptions import PromptNotPresent, UnknownSiteChosen
from pyba.utils.load_yaml import load_config

config = load_config("general")


class Engine(BaseEngine):
    """
    The main entrypoint for browser automation. This engine exposes the main entry point which is the run() method

    Args:
        `openai_api_key`: API key for OpenAI models should you want to use that
        `vertexai_project_id`: Create a VertexAI project to use that instead of OpenAI
        `vertexai_server_location`: VertexAI server location
        `gemini_api_key`: API key for Gemini-2.5-pro native support without VertexAI
        `headless`: Choose if you want to run in the headless mode or not
        `handle_dependencies`: Choose if you want to automatically install dependencies during runtime
        `use_logger`: Choose if you want to use the logger (that is enable logging of data)
        `enable_tracing`: Choose if you want to enable tracing. This will create a .zip file which you can use in traceviewer
        `trace_save_directory`: The directory where you want the .zip file to be saved

        `database`: An instance of the Database class which will define all database specific configs

    Find these default values at `pyba/config.yaml`.

    The `Engine` is inherited off from the `BaseEngine`. The BaseEngine handles the common methods for
    all the modes (default, DFS and BFS). The main `Engine` decides if execution needs to be passed to a different
    mode depending on what is set by the user.

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
        self.mode = "Normal"
        # Passing the common setup to the BaseEngine
        super().__init__(
            headless=headless,
            enable_tracing=enable_tracing,
            trace_save_directory=trace_save_directory,
            database=database,
            use_logger=use_logger,
            mode=self.mode,
            handle_dependencies=handle_dependencies,
            openai_api_key=openai_api_key,
            vertexai_project_id=vertexai_project_id,
            vertexai_server_location=vertexai_server_location,
            gemini_api_key=gemini_api_key,
        )

        # session_id stays here becasue BaseEngine will be inherited by many
        self.session_id = uuid.uuid4().hex

        selectors = tuple(config["process_config"]["selectors"])
        self.combined_selector = ", ".join(selectors)

    async def run(self, prompt: str = None, automated_login_sites: List[str] = None):
        """
        The most basic implementation for the run function

        Args:
            `prompt`: The user's instructions
                Right now we're assuming that the user's prompt is well defined. In later
                versions we'll come up with a fix for that as well.
        """

        # print(type(self.planner_agent.generate(task=prompt)))     List in case of BFS and string in case of DFS

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

            self.context = await self.get_trace_context()
            self.page = await self.context.new_page()
            cleaned_dom = await initial_page_setup(self.page)

            for steps in range(0, config["main_engine_configs"]["max_iteration_steps"]):
                # If LoginEngines have been chosen then self.automated_login_engine_classes will be populated
                login_attempted_successfully = await self.attempt_login()
                if login_attempted_successfully:
                    cleaned_dom = await self.successful_login_clean_and_get_dom()
                    # Jump to the next iteration of the loop
                    continue

                # Get an actionable PlaywrightResponse from the models
                history = self.fetch_history()
                action = self.fetch_action(
                    cleaned_dom=cleaned_dom.to_dict(), user_prompt=prompt, history=history
                )
                output = await self.generate_output(
                    action=action, cleaned_dom=cleaned_dom, prompt=prompt
                )

                if output:
                    await self.save_trace()
                    await self.shut_down()
                    return output

                self.log.action(action)

                if self.db_funcs:
                    self.db_funcs.push_to_episodic_memory(
                        session_id=self.session_id, action=str(action), page_url=str(self.page.url)
                    )
                # If its not None, then perform it
                value, fail_reason = await perform_action(self.page, action)

                if value is None:
                    # This means the action failed due to whatever reason. The best bet is to
                    # pass in the latest cleaned_dom and get the output again
                    cleaned_dom = await self.extract_dom()
                    output = await self.retry_perform_action(
                        cleaned_dom=cleaned_dom.to_dict(),
                        prompt=prompt,
                        history=history,
                        fail_reason=fail_reason,
                    )

                    if output:
                        await self.save_trace()
                        await self.shut_down()
                        return output

                # Else, get the new DOM and restart loop
                cleaned_dom = await self.extract_dom()

        await self.save_trace()
        await self.shut_down()

    def sync_run(
        self, prompt: str = None, automated_login_sites: List[str] = None
    ) -> Union[str, None]:
        """
        Sync endpoint for running the above function
        """
        output = asyncio.run(self.run(prompt=prompt, automated_login_sites=automated_login_sites))

        if output:
            return output
