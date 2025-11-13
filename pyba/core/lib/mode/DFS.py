from typing import List

from pyba.core.lib import BaseEngine
from pyba.logger import get_logger
from pyba.utils.load_yaml import load_config

config = load_config("general")["main_engine_configs"]


class DFS(BaseEngine):
    """
    Methods for handling DFS exploratory searches. The `BaseEngine` initialises
    the provider and with that the planner and playwright agents.

    Args:
            `plan`: A single plan that needs to be executed in depth
            `prompt`: The prompt given by the user

    The `max_depth` is initialised to ensure that we don't get out of control.

    Mechanism:

        - Take the planner agent and the playwright agent from the main `Engine`
        - Run the planner agent to obtain a single plan to be performed
    """

    def __init__(self, user_prompt: str, automated_login_sites: List):
        self.user_prompt = user_prompt

        self.log = get_logger()

        self.max_depth = config["max_depth"]

    async def run(self):
        """
        Run pyba in DFS mode.
        """
        pass
