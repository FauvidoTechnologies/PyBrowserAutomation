import json
from types import SimpleNamespace
from typing import Dict, List, Union

from google import genai
from google.genai.types import GenerateContentConfig
from openai import OpenAI

from pyba.utils.load_yaml import load_config
from pyba.utils.prompts import (
    system_instruction,
    general_prompt,
    output_system_instruction,
    output_prompt,
)
from pyba.utils.structure import PlaywrightResponse, OutputResponseFormat

config = load_config("general")


class PlaywrightAgent:
    """
    The automation main engine. This takes in all the context from
    the current screen and decides the next best action. We're
    supporting two APIs for now:

    1. VertexAI projects
    2. OpenAI

    Depending on which key you have set in the main engine, this agent
    will be called. This configuration is taken directly from the engine.
    We're not making this an inherited class of Engine because this is
    technically not an Engine per se, its is own thing.
    """

    def __init__(self, engine) -> None:
        """
        `engine` basically holds all the arguments from the
        """
        self.engine = engine
        self.initialize_playwright_agent()

    def initialize_playwright_agent(self) -> None:
        """
        Initialises a client/agent depending on the provider
        """
        if self.engine.provider == "openai":
            self.openai_client = OpenAI(api_key=self.engine.openai_api_key)
            self.agent = {
                "client": self.openai_client,
                "system_instruction": system_instruction,
                "output_system_instruction": output_system_instruction,
                "model": config["main_engine_configs"]["openai"]["model"],
                "response_format": PlaywrightResponse,
                "output_response_format": OutputResponseFormat,
            }
        else:
            self.vertexai_client = genai.Client(
                vertexai=True,
                project=self.engine.vertexai_project_id,
                location=self.engine.location,
            )

            self.agent = self.vertexai_client.chats.create(
                model=self.engine.model,
                config=GenerateContentConfig(
                    temperature=0,
                    system_instruction=system_instruction,
                    response_schema=PlaywrightResponse,
                    response_mime_type="application/json",
                ),
            )

            self.output_agent = self.vertexai_client.chats.create(
                model=self.engine.model,
                config=GenerateContentConfig(
                    temperature=0,
                    system_instruction=output_system_instruction,
                    response_schema=OutputResponseFormat,
                    response_mime_type="application/json",
                ),
            )

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
        cleaned_dom["user_prompt"] = user_prompt
        prompt = general_prompt.format(**cleaned_dom)

        if self.engine.provider == "openai":
            messages = [
                {"role": "system", "content": self.agent["system_instruction"]},
                {"role": "user", "content": prompt},
            ]
            kwargs = {
                "model": self.agent["model"],
                "messages": messages,
            }
            # This is when we are passing a response scehma to the model. We use the .parse() endpoint
            response = self.agent["client"].chat.completions.parse(
                **kwargs, response_format=self.agent["response_format"]
            )
            return SimpleNamespace(
                **json.loads(response.choices[0].message.content).get("actions")[0]
            )
        else:
            response = self.agent.send_message(prompt)
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
        print("inside")
        cleaned_dom["user_prompt"] = user_prompt

        # Passing only the hyperlinks, actual text and user_prompt inside the prompt
        prompt = output_prompt.format(**cleaned_dom)

        if self.engine.provider == "openai":
            messages = [
                {"role": "system", "content": self.agent["output_system_instruction"]},
                {"role": "user", "content": prompt},
            ]

            kwargs = {
                "model": self.agent["model"],
                "messages": messages,
            }

            response = self.agent["client"].chat.completions.parse(
                **kwargs, response_format=self.agent["output_response_format"]
            )

            return str(json.loads(response.choices[0].message.content).get("output"))
        else:
            response = self.output_agent.send_message(prompt)
            print(f"This is the actual response: {response}")
            try:
                output = getattr(response, "output_parsed", getattr(response, "parsed", None))

                if output and hasattr(output, "output") and output.output:
                    return output.output

                raise IndexError("No output found in the response!")

            except Exception as e:
                print(f"Unable to parse the output from VertexAI response: {e}")
