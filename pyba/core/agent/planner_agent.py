import json
import time
from typing import Union, Dict, List, Any

from pyba.core.agent.llm_factory import LLMFactory
from pyba.logger import get_logger
from pyba.utils.load_yaml import load_config
from pyba.utils.prompts import planner_general_prompt_DFS, planner_general_prompt_BFS
from pyba.utils.retry import Retry
from pyba.utils.structure import PlannerAgentOutputBFS, PlannerAgentOutputDFS

config = load_config("general")["main_engine_configs"]


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
        self.mode = self.engine.mode

        self.agent = self.llm_factory.get_planner_agent()

        self.max_breadth = config["max_breadth"]

    def _initialise_prompt(self, task: str, old_plan: str = None):
        """
                Initialise the prompt for the planner agent

        Args:
                `task`: Task given by the user
                `old_plan`: The previous plan in case of DFS mode
        """
        if self.mode == "BFS":
            return planner_general_prompt_BFS.format(task=task, max_plans=self.max_breadth)
        else:
            return planner_general_prompt_DFS.format(task=task, old_plan=old_plan)

    def _initialise_openai_arguments(
        self, system_instruction: str, task: str, model_name: str
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Initialises the arguments for OpenAI agents

        Args:
            `system_instruction`: The system instruction for the agent
            `task`: The current task for the model to perform
            `model_name`: The OpenAI model name

        Returns:
            An arguments dictionary which can be directly passed to OpenAI agents
        """

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": task},
        ]

        kwargs = {
            "model": model_name,
            "messages": messages,
        }

        return kwargs

    def _call_model(self, agent: Any, prompt: str) -> Any:
        """
        Generic method to call the correct LLM provider and parse the response.

        Args:
            agent: The agent to use (action_agent or output_agent)
            prompt: The fully formatted prompt string

        Returns:
            The parsed response (SimpleNamespace for action, str for output)

        Uses the attempt_number to give ou
        """
        if self.engine.provider == "openai":
            arguments = self._initialise_openai_arguments(
                system_instruction=agent["system_instruction"],
                task=prompt,
                model_name=agent["model"],
            )

            while True:
                try:
                    response = agent["client"].chat.completions.parse(
                        **arguments, response_format=agent["response_format"]
                    )
                    self.attempt_number = 1
                    break
                except Exception:
                    # If we hit a rate limit, calculate the time to wait and retry
                    wait_time = self.calculate_next_time(self.attempt_number)
                    self.log.warning(
                        f"Hit the rate limit for OpenAI, retrying in {wait_time} seconds"
                    )
                    time.sleep(wait_time)  # wait_time is in seconds
                    self.attempt_number += 1

            parsed_json = json.loads(response.choices[0].message.content)

            if "plans" in list(parsed_json.keys()):
                return parsed_json["plans"]
            if "plan" in list(parsed_json.keys()):
                return parsed_json["plan"]
            self.log.error("Parsed object has neither 'plans' nor 'plan' attribute.")
            return None

        elif self.engine.provider == "vertexai":  # VertexAI logic
            while True:
                try:
                    response = agent.send_message(prompt)
                    self.attempt_number = 1
                    break
                except Exception:
                    wait_time = self.calculate_next_time(self.attempt_number)
                    self.log.warning(
                        f"Hit the rate limit for VertexAI, retrying in {wait_time} seconds"
                    )
                    time.sleep(wait_time)
                    self.attempt_number += 1
            try:
                parsed_object = getattr(
                    response, "output_parsed", getattr(response, "parsed", None)
                )

                if not parsed_object:
                    self.log.error("No parsed object found in VertexAI response.")
                    return None

                if hasattr(parsed_object, "plans"):
                    return parsed_object.plans

                if hasattr(parsed_object, "plan"):
                    return parsed_object.plan

                self.log.error("Parsed object has neither 'plans' nor 'plan' attribute.")
                return None

            except Exception as e:
                self.log.error(f"Unable to parse the output from VertexAI response: {e}")
                return None

        else:  # Using gemini
            gemini_config = {
                "response_mime_type": "application/json",
                "response_json_schema": agent["response_format"].model_json_schema(),
                "system_instruction": agent["system_instruction"],
            }

            while True:
                try:
                    response = agent["client"].models.generate_content(
                        model=agent["model"],
                        contents=prompt,
                        config=gemini_config,
                    )
                    self.attempt_number = 1
                    break
                except Exception:
                    wait_time = self.calculate_next_time(self.attempt_number)
                    self.log.warning(
                        f"Hit the rate limit for Gemini, retrying in {wait_time} seconds"
                    )
                    time.sleep(wait_time)
                    self.attempt_number += 1

            action = agent["response_format"].model_validate_json(response.text)

            if hasattr(action, "plan"):
                return action.plan

            elif hasattr(action, "plans"):
                return action.plans

            else:
                self.log.error("Parsed object has neither 'plans' nor 'plan' attribute.")
                return None

    def generate(
        self, task: str, old_plan: str = None
    ) -> Union[PlannerAgentOutputBFS, PlannerAgentOutputDFS]:
        """
        Endpoint to generate the plan(s) depending on the set mode (the agent encodes the mode)

        Args:
            `task`: The task provided by the user
            `old_plan`: The previous plan if using DFS mode

        Function:
            - Takes in the user prompt which serves as the task for the model to perform
            - Depending on DFS or BFS mode generates plan(s)
        """
        prompt = self._initialise_prompt(task=task, old_plan=old_plan)
        return self._call_model(agent=self.agent, prompt=prompt)
