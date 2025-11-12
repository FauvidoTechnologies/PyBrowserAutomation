import json
import time
from types import SimpleNamespace
from typing import Dict, List, Union, Any

from pyba.core.agent.llm_factory import LLMFactory
from pyba.logger import get_logger
from pyba.utils.prompts import general_prompt, output_prompt
from pyba.utils.retry import Retry
from pyba.utils.structure import PlaywrightResponse


class PlaywrightAgent(Retry):
    """
    Defines the playwright agent's actions

    Provides two endpoints:
        - `process_action`: for returning the right action on a page
        - `get_output`: for summarizing the chat and returning a string
    """

    def __init__(self, engine) -> None:
        """
        Args:
            `engine`: holds all the arguments from the user

        Initialises the agents using the `.get_agent()` entrypoint from the LLMFactory
        """
        super().__init__()  # Initiaising the retry variables
        self.attempt_number = 1
        self.engine = engine
        self.llm_factory = LLMFactory(engine=self.engine)

        self.log = get_logger()
        self.action_agent, self.output_agent = self.llm_factory.get_agent()

    def _initialise_prompt(
        self,
        cleaned_dom: Dict[str, Union[List, str]],
        user_prompt: str,
        main_instruction: str,
        history: List[str] = None,
        fail_reason: str = None,
    ):
        """
        Method to initailise the main instruction for any agent

        Args:
            `cleaned_dom`: A dictionary containing nicely formatted DOM elements
            `user_prompt`: The instructions given by the user
            `main_instruction`: The prompt for the playwright agent
            `history`: An episodic memory of all the successfully executed tasks
            `fail_reason`: The reason for the failure of the previous action

        The fail_reason decides if the previous access was a success or not.
        """

        # Adding the user_prompt to the DOM to make it easier to format the prompt
        cleaned_dom["user_prompt"] = user_prompt
        cleaned_dom["history"] = history

        if fail_reason:
            cleaned_dom["action_output"] = fail_reason
            cleaned_dom["history_type"] = "failure"
        else:
            cleaned_dom["action_output"] = "Success"
            cleaned_dom["history_type"] = "success"

        prompt = main_instruction.format(**cleaned_dom)

        return prompt

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

    def _call_model(self, agent: Any, prompt: str, agent_type: str) -> Any:
        """
        Generic method to call the correct LLM provider and parse the response.

        Args:
            agent: The agent to use (action_agent or output_agent)
            prompt: The fully formatted prompt string
            agent_type: "action" or "output", to determine parsing logic

        Returns:
            The parsed response (SimpleNamespace for action, str for output)

        Uses the attempt_number to give ou
        """
        if self.engine.provider == "openai":
            arguments = self._initialise_openai_arguments(
                system_instruction=agent["system_instruction"],
                prompt=prompt,
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

            # Parse based on agent type
            if agent_type == "action":
                return SimpleNamespace(**parsed_json.get("actions")[0])
            elif agent_type == "output":
                return str(parsed_json.get("output"))

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

                # Parse based on agent type
                if agent_type == "action":
                    if hasattr(parsed_object, "actions") and parsed_object.actions:
                        return parsed_object.actions[0]
                    raise IndexError("No 'actions' found in VertexAI response.")
                elif agent_type == "output":
                    if hasattr(parsed_object, "output") and parsed_object.output:
                        return str(parsed_object.output)
                    raise IndexError("No 'output' found in VertexAI response.")

            except Exception as e:
                if not response:
                    self.log.error(f"Unable to parse the output from VertexAI response: {e}")
                # If we have a response which cannot be parsed, it MUST be a None value

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
            return action.actions[0]

    def process_action(
        self,
        cleaned_dom: Dict[str, Union[List, str]],
        user_prompt: str,
        history: List[str] = None,
        fail_reason: str = None,
    ) -> PlaywrightResponse:
        """
        Method to process the DOM and provide an actionable playwright response

        Args:
            `cleaned_dom`: Dictionary of the extracted items from the DOM
                - `hyperlinks`: List
                - `input_fields` (basically all fillable boxes): List
                - `clickable_fields`: List
                - `actual_text`: string
            `user_prompt`: The instructions given by the user
            `history`: An episodic memory of all the successfully executed tasks
            `fail_reason`: Holds the fail-reason should the previous task fail

            We're assuming this to be well explained. In later versions we'll
            add one more layer on top for plan generation and better commands

            output: A predefined pydantic model
        """

        prompt = self._initialise_prompt(
            cleaned_dom=cleaned_dom,
            user_prompt=user_prompt,
            main_instruction=general_prompt,
            history=history,
            fail_reason=fail_reason,
        )

        return self._call_model(agent=self.action_agent, prompt=prompt, agent_type="action")

    def get_output(self, cleaned_dom: Dict[str, Union[List, str]], user_prompt: str) -> str:
        """
        Method to get the final output from the model if the user requested for one
        """

        prompt = self._initialise_prompt(
            cleaned_dom=cleaned_dom, user_prompt=user_prompt, main_instruction=output_prompt
        )

        return self._call_model(agent=self.output_agent, prompt=prompt, agent_type="output")
