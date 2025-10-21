import json
from types import SimpleNamespace
from typing import Dict, List, Union

from google import genai
from google.genai.types import GenerateContentConfig
from openai import OpenAI

from pyba.utils.prompts import system_instruction, general_prompt
from pyba.utils.structure import PlaywrightResponse


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
                "model": "gpt-4o",
                "response_format": PlaywrightResponse,
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

        print()
        print(cleaned_dom)
        print()

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
