import random
from typing import Literal, Dict, List

from pyba.core.agent.llm_factory import LLMFactory
from pyba.logger import get_logger


class BaseAgent:
    """
    The base class for all Agents to define common methods

        Contains methods for exponential backoff and retry as well
        Note: this backoff and retry will be blocking for that specific context.

    Defines the following variables:

    `exponential_base`: 2 (we're using base 2)
    `base_timeout`: 1 second
    `max_backoff_time`: 60 seconds
    `LLMFactory`: The internal agent call is made by agent itself.
    `log`: The logger for the agents
    """

    def __init__(self, engine):
        self.base = 2
        self.base_timeout = 1
        self.max_backoff_time = 60

        self.engine = engine
        self.llm_factory = LLMFactory(engine=self.engine)
        self.log = get_logger()
        self.mode: Literal["Normal", "DFS", "BFS"] = self.engine.mode

    def _initialise_openai_arguments(
        self, system_instruction: str, prompt: str, model_name: str
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Initialises the arguments for OpenAI agents

        Args:
            `system_instruction`: The system instruction for the agent
            `prompt`: The current prompt for the agent
            `model_name`: The OpenAI model name

        Returns:
            An arguments dictionary which can be directly passed to OpenAI agents
        """

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ]

        kwargs = {
            "model": model_name,
            "messages": messages,
        }

        return kwargs

    def calculate_next_time(self, attempt_number):
        """
        Function to calculate the next wait time in seconds

        Args:
                `attempt_number`: The number of failed attempts
        """

        delay = self.base_timeout * (self.base ** (attempt_number - 1))
        delay = min(delay, self.max_backoff_time)
        jitter = random.uniform(0, delay / 2)
        return delay + jitter
