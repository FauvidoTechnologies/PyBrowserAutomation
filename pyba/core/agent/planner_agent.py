from typing import Union

from pyba.core.agent.llm_factory import LLMFactory
from pyba.logger import get_logger
from pyba.utils.retry import Retry
from pyba.utils.structure import PlannerAgentOutputBFS, PlannerAgentOutputDFS


class PlannerAgent(Retry):
    """
    Planner agent for DFS and BFS modes under exploratory cases. This is inheriting off
    from the Retry class as well and supports all agents under LLM_factory.

    Args:
            `engine`: Engine to hold all arguments provided by the user
    """

    def __init__(self, engine) -> None:
        """
        Initialises the right agent from the LLMFactory

        - Uses the .get_planner_agent() endpoint in the LLMFactory to initialise the right system prompts
        """
        super().__init__()  # Initialising the retry variables
        self.attempt_number = 1
        self.engine = engine
        self.llm_factory = LLMFactory(engine=self.engine)  # The engine variable holds the mode

        self.log = get_logger()

        self.agent = self.llm_factory.get_planner_agent()

    def generate(self) -> Union[PlannerAgentOutputBFS, PlannerAgentOutputDFS]:
        """
        Endpoint to generate the plan(s) depending on the set mode (the agent encodes the mode)

        Function:
                Takes in the user prompt which serves as the instruction for any future
        """

        pass
