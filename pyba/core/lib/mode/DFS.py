from pyba.core.lib import BaseEngine
from pyba.logger import get_logger
from pyba.utils.load_yaml import load_config

config = load_config("general")["main_engine_configs"]


class DFS(BaseEngine):
    """
    Methods for handling DFS exploratory searches

    Args:
            `plan`: A single plan that needs to be executed in depth
            `prompt`: The prompt given by the user

    The `max_depth` is initialised to ensure that we don't get out of control. The revert
    mechanism is explained in the README.
    """

    def __init__(self, plan: str, prompt: str):
        self.plan = plan
        self.prompt = prompt

        self.log = get_logger()

        self.max_depth = config["max_depth"]

    def start_scan(self):
        pass
