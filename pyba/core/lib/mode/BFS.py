import asyncio
import uuid
from typing import List, Union

from pyba.core.agent import PlannerAgent
from pyba.core.lib.mode.base import BaseEngine
from pyba.database import Database
from pyba.utils.load_yaml import load_config

config = load_config("general")


class BFS(BaseEngine):
    """
    Methods for handling DFS exploratory searches. The `BaseEngine` initialises
    the provider and with that the playwright action and output agents.

    This is another entry point engine and can be directly imported by the user.

    The following params are defined:

    Args:
        `openai_api_key`: API key for OpenAI models should you want to use that
        `vertexai_project_id`: Create a VertexAI project to use that instead of OpenAI
        `vertexai_server_location`: VertexAI server location
        `gemini_api_key`: API key for Gemini-2.5-pro native support without VertexAI
        `headless`: Choose if you want to run in the headless mode or not
        `handle_dependencies`: Choose if you want to automatically install dependencies during runtime
        `use_logger`: Choose if you want to use the logger (that is enable logging of data)
        `max_depth`: The maximum depth to go into for each plan, where each level of depth corresponds to an action
        `max_breadth`: The number of plans to execute one by one in depth
        `enable_tracing`: Choose if you want to enable tracing. This will create a .zip file which you can use in traceviewer
        `trace_save_directory`: The directory where you want the .zip file to be saved

        `database`: An instance of the Database class which will define all database specific configs

    Find these default values at `pyba/config.yaml`.
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
        max_depth: int = config["main_engine_configs"]["max_depth"],
        max_breadth: int = config["main_engine_configs"]["max_depth"],
        enable_tracing: bool = config["main_engine_configs"]["enable_tracing"],
        trace_save_directory: str = None,
        database: Database = None,
    ):
        self.mode = "DFS"
        # Passing the common setup to the BaseEngine
        super().__init__(
            headless=headless,
            enable_tracing=enable_tracing,
            trace_save_directory=trace_save_directory,
            database=database,
            use_logger=use_logger,
            mode=self.mode,
            openai_api_key=openai_api_key,
            vertexai_project_id=vertexai_project_id,
            vertexai_server_location=vertexai_server_location,
            gemini_api_key=gemini_api_key,
        )

        # session_id stays here becasue BaseEngine will be inherited by many
        self.session_id = uuid.uuid4().hex

        selectors = tuple(config["process_config"]["selectors"])
        self.combined_selector = ", ".join(selectors)
        self.planner_agent = PlannerAgent(engine=self)

        self.max_depth = max_depth
        self.max_breadth = max_depth

    async def run(self, prompt: str, automated_login_sites: List[str] = None) -> Union[str, None]:
        """
        Run pyba in DFS mode.
        """
        plan = self.planner_agent.generate(task=prompt)
        self.log.info(f"This is the plan for a DFS: {plan}")

        # TODO: Finish this
        pass

    def sync_run(self, prompt: str, automated_login_sites: List[str] = None) -> Union[str, None]:
        """
        Sync endpoint for running the above function
        """
        output = asyncio.run(self.run(prompt=prompt, automated_login_sites=automated_login_sites))

        if output:
            return output
