import json
from types import SimpleNamespace
from typing import Dict, List, Union

from pyba.core.agent.llm_factory import LLMFactory
from pyba.utils.prompts import general_prompt, output_prompt
from pyba.utils.structure import PlaywrightResponse


class PlaywrightAgent:
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
        self.engine = engine
        self.llm_factory = LLMFactory(engine=self.engine)

        self.action_agent, self.output_agent = self.llm_factory.get_agent()

    def _initialise_prompt(
        self, cleaned_dom: Dict[str, Union[List, str]], user_prompt: str, main_instruction: str
    ):
        """
        Method to initailise the main instruction for any agent

        Args:
            `cleaned_dom`: A dictionary containing nicely formatted DOM elements
            `user_prompt`: The instructions given by the user
            `main_instruction`: The prompt for the playwright agent
        """

        # Adding the user_prompt to the DOM to make it easier to format the prompt
        cleaned_dom["user_prompt"] = user_prompt
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

    def process_action(
        self, cleaned_dom: Dict[str, Union[List, str]], user_prompt: str
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

            We're assuming this to be well explained. In later versions we'll
            add one more layer on top for plan generation and better commands

            output: A predefined pydantic model
        """
        prompt = self._initialise_prompt(
            cleaned_dom=cleaned_dom, user_prompt=user_prompt, main_instruction=general_prompt
        )

        if self.engine.provider == "openai":
            arguments = self._initialise_openai_arguments(
                system_instruction=self.action_agent["system_instruction"],
                prompt=prompt,
                model_name=self.action_agent["model"],
            )

            # Using the .parse() endpoint for the `response_format`
            response = self.action_agent["client"].chat.completions.parse(
                **arguments, response_format=self.action_agent["response_format"]
            )
            return SimpleNamespace(
                **json.loads(response.choices[0].message.content).get("actions")[0]
            )
        else:
            # In VertexAI, the `send_message` endpoint does not require any additional configurations
            response = self.action_agent.send_message(prompt)
            try:
                # We should prefer .output_parsed if using google-genai structured output
                actions = getattr(response, "output_parsed", getattr(response, "parsed", None))
                if actions and hasattr(actions, "actions") and actions.actions:
                    return actions.actions[0]
                raise IndexError("No actions found in response.")
            except Exception as e:
                print(f"Unable to parse the output from VertexAI response: {e}")

    def get_output(self, cleaned_dom: Dict[str, Union[List, str]], user_prompt: str) -> str:
        """
        Method to get the final output from the model if the user requested for one
        """

        prompt = self._initialise_prompt(
            cleaned_dom=cleaned_dom, user_prompt=user_prompt, main_instruction=output_prompt
        )

        if self.engine.provider == "openai":
            arguments = self._initialise_openai_arguments(
                system_instruction=self.output_agent["system_instruction"],
                prompt=prompt,
                model_name=self.output_agent["model"],
            )

            response = self.output_agent["client"].chat.completions.parse(
                **arguments, response_format=self.output_agent["output_response_format"]
            )

            return str(json.loads(response.choices[0].message.content).get("output"))
        else:
            response = self.output_agent.send_message(prompt)
            try:
                output = getattr(response, "output_parsed", getattr(response, "parsed", None))

                if output and hasattr(output, "output") and output.output:
                    return output.output

                print("No output found in the response!")

            except Exception as e:
                print(f"Unable to parse the output from VertexAI response: {e}")
